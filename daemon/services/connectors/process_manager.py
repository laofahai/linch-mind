"""
Process manager for connector processes with lock mechanism.
Prevents duplicate process spawning and manages process lifecycle.
"""
import os
import psutil
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ProcessManager:
    """Unified process manager to prevent duplicate process spawning."""
    
    def __init__(self):
        self.lock_dir = Path.home() / ".linch-mind" / "locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ProcessManager initialized with lock directory: {self.lock_dir}")
    
    def acquire_lock(self, connector_id: str, instance_id: Optional[str] = None) -> bool:
        """
        Acquire process lock to prevent duplicate processes.
        
        Args:
            connector_id: The connector type ID
            instance_id: Optional instance ID for multiple instances
            
        Returns:
            True if lock acquired, False if process already running
        """
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"
        
        # Check if lock file exists
        if lock_file.exists():
            try:
                pid = int(lock_file.read_text())
                if self._is_process_running(pid):
                    logger.warning(f"Process already running for {lock_name} (PID: {pid})")
                    return False
                # Process is dead, clean up lock file
                logger.info(f"Cleaning up stale lock for {lock_name} (PID: {pid})")
                lock_file.unlink()
            except (ValueError, OSError) as e:
                logger.error(f"Error reading lock file for {lock_name}: {e}")
                lock_file.unlink()
        
        # Create new lock
        current_pid = os.getpid()
        lock_file.write_text(str(current_pid))
        logger.info(f"Lock acquired for {lock_name} (PID: {current_pid})")
        return True
    
    def release_lock(self, connector_id: str, instance_id: Optional[str] = None):
        """Release process lock."""
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"
        
        if lock_file.exists():
            try:
                lock_file.unlink()
                logger.info(f"Lock released for {lock_name}")
            except OSError as e:
                logger.error(f"Error releasing lock for {lock_name}: {e}")
    
    def is_locked(self, connector_id: str, instance_id: Optional[str] = None) -> bool:
        """Check if a connector is locked (running)."""
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"
        
        if not lock_file.exists():
            return False
        
        try:
            pid = int(lock_file.read_text())
            return self._is_process_running(pid)
        except (ValueError, OSError):
            return False
    
    def get_running_pid(self, connector_id: str, instance_id: Optional[str] = None) -> Optional[int]:
        """Get PID of running connector process."""
        lock_name = f"{connector_id}_{instance_id}" if instance_id else connector_id
        lock_file = self.lock_dir / f"{lock_name}.lock"
        
        if not lock_file.exists():
            return None
        
        try:
            pid = int(lock_file.read_text())
            if self._is_process_running(pid):
                return pid
        except (ValueError, OSError):
            pass
        
        return None
    
    def cleanup_zombies(self):
        """Clean up all zombie processes and stale locks."""
        cleaned_count = 0
        
        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                pid = int(lock_file.read_text())
                if not self._is_process_running(pid):
                    lock_file.unlink()
                    logger.info(f"Cleaned up stale lock: {lock_file.name} (PID: {pid})")
                    cleaned_count += 1
            except (ValueError, OSError) as e:
                logger.error(f"Error cleaning up lock {lock_file.name}: {e}")
                try:
                    lock_file.unlink()
                    cleaned_count += 1
                except OSError:
                    pass
        
        logger.info(f"Cleaned up {cleaned_count} stale locks")
        return cleaned_count
    
    def _is_process_running(self, pid: int) -> bool:
        """Check if a process with given PID is running."""
        try:
            process = psutil.Process(pid)
            # Check if it's actually a Python process (our connector)
            return process.is_running() and 'python' in process.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def kill_process(self, connector_id: str, instance_id: Optional[str] = None) -> bool:
        """
        Kill a running connector process.
        
        Returns:
            True if process was killed, False if not found
        """
        pid = self.get_running_pid(connector_id, instance_id)
        if not pid:
            return False
        
        try:
            process = psutil.Process(pid)
            process.terminate()
            logger.info(f"Terminated process for {connector_id} (PID: {pid})")
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if not terminated
                process.kill()
                logger.warning(f"Force killed process for {connector_id} (PID: {pid})")
            
            # Release lock
            self.release_lock(connector_id, instance_id)
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error killing process for {connector_id}: {e}")
            # Clean up lock anyway
            self.release_lock(connector_id, instance_id)
            return False
    
    def list_running_connectors(self) -> list[dict]:
        """List all running connector processes."""
        running = []
        
        for lock_file in self.lock_dir.glob("*.lock"):
            try:
                pid = int(lock_file.read_text())
                if self._is_process_running(pid):
                    # Parse connector info from lock filename
                    lock_name = lock_file.stem
                    parts = lock_name.split('_', 1)
                    connector_id = parts[0]
                    instance_id = parts[1] if len(parts) > 1 else None
                    
                    # Get process info
                    process = psutil.Process(pid)
                    
                    running.append({
                        'connector_id': connector_id,
                        'instance_id': instance_id,
                        'pid': pid,
                        'create_time': process.create_time(),
                        'memory_info': process.memory_info()._asdict(),
                        'cpu_percent': process.cpu_percent(interval=0.1)
                    })
            except (ValueError, OSError, psutil.Error) as e:
                logger.error(f"Error checking lock {lock_file.name}: {e}")
        
        return running


# Global instance
_process_manager = None


def get_process_manager() -> ProcessManager:
    """Get or create the global ProcessManager instance."""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
        # Clean up any stale locks on initialization
        _process_manager.cleanup_zombies()
    return _process_manager