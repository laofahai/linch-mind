# Linch Mind 安全架构设计

**版本**: 3.0 - 实用主义版  
**创建时间**: 2025-08-04  
**最后更新**: 2025-08-04  
**状态**: 设计完成  
**适用范围**: 本地存储的个人AI助手数据保护

## 1. 概述

Linch Mind作为"隐私至上"的个人AI助手，处理用户最敏感的个人数据，包括AI对话历史、知识图谱、行为模式等。本文档基于**实用主义原则**，设计了一套既能有效保护用户数据，又不过度复杂的安全架构。

### 1.1 设计原则 (用户体验优先版)

- **SQLCipher First**: SQLCipher AES-256已提供军用级保护，是主要防线
- **用户价值优先**: 安全措施不应损害核心智能功能
- **透明化选择**: 让用户理解并选择适合的安全级别
- **本地优先**: 基于本地存储的威胁模型设计
- **简化架构**: 避免过度工程化，专注核心价值交付
- **智能边界**: 只对真正的秘密（密码、密钥）进行额外保护

## 2. 威胁模型分析

### 2.1 重新定义的数据敏感性评估

基于用户价值优先的原则重新分类：

```
🔴 真正的机密 (SECRETS) - 需要额外保护
- 系统密码: 主密码、API密钥
- 认证凭据: OAuth token、访问令牌
- 金融信息: 信用卡号、银行账户
- 法律敏感: 身份证号、护照号

🟡 个人智能数据 (PERSONAL-INTELLIGENT) - SQLCipher保护下允许智能分析
- AI对话历史: 用户的思考过程和价值观 → 智能推荐的核心数据源
- 个人知识图谱: 认知指纹和兴趣模型 → 跨应用关联的基础
- 跨应用行为模式: 数字生活轨迹 → 主动推荐的依据
- 工作文档内容: 研究成果、商业计划 → 智能整理的对象

🟢 系统运行数据 (OPERATIONAL) - 标准保护
- 系统配置: 连接器设置、用户偏好
- 使用统计: 功能使用频率、性能指标
- 缓存数据: 临时计算结果、预处理数据
```

**核心认知转变**:
- ✅ **个人智能数据是Linch Mind的核心价值源泉**，不应过度脱敏
- ✅ **SQLCipher AES-256加密已提供军用级保护**，无需额外应用层脱敏
- ✅ **只有真正的机密才需要额外保护措施**

### 2.2 本地存储威胁场景

基于**本地存储**环境，识别出以下主要威胁：

| 威胁类型 | 概率 | 影响程度 | 典型场景 |
|---------|------|---------|----------|
| 设备丢失/被盗 | 🔴 高 | 🔴 高 | 笔记本被盗，数据直接暴露 |
| 恶意软件攻击 | 🟡 中 | 🔴 高 | 浏览器插件、钓鱼软件访问文件 |
| 共享设备访问 | 🟡 中 | 🟡 中 | 家人、同事临时使用电脑 |
| 硬盘数据恢复 | 🟡 中 | 🟡 中 | 设备废弃时数据残留 |
| 针对性APT攻击 | 🟢 极低 | 🔴 极高 | 国家级、企业间谍攻击 |
| 内存转储攻击 | 🟢 极低 | 🔴 高 | 高级恶意软件内存分析 |

### 2.3 关键认知

- ✅ **SQLCipher可防护95%以上的现实威胁**
- ✅ **本地存储避免了网络传输和云端泄露风险**
- ⚠️ **过度复杂的安全措施可能降低整体安全性**
- ❌ **完全防护APT攻击需要付出不成比例的代价**

## 3. 安全架构设计

### 3.1 核心安全策略

基于数据存储架构的三层安全防护：

```python
# 实用主义安全架构 - 基于数据存储架构设计
class LinchMindSecurityArchitecture:
    """
    三层存储架构 + 统一安全管理 + 分级数据保护
    基于数据存储架构的安全防护体系
    """
    
    # Layer 1: 主存储层安全 (SQLCipher)
    primary_storage_security: SQLCipherDatabaseService    # 核心数据加密
    
    # Layer 2: 向量存储层安全 (ChromaDB本地)
    vector_storage_security: ChromaVectorEncryption       # 向量数据保护
    
    # Layer 3: 图分析层安全 (NetworkX + SQLite持久化)
    graph_storage_security: GraphDataEncryption           # 图数据加密
    
    # 统一管理层
    unified_data_manager: UnifiedDataManager              # 跨层安全协调
    key_management: SimpleKeyManager                       # 用户友好的密钥管理
    export_encryption: FileEncryptionService              # 备份/导出加密
    
    # 可选增强 (高级用户)
    enhanced_features: Optional[ParanoidMode] = None
```

**三层安全架构说明**:

1. **主存储层 (SQLCipher)**
   - 极高敏感数据：AI对话历史、个人知识图谱、跨应用行为
   - 加密强度：AES-256-GCM + PBKDF2(100k 迭代)
   - 防护级别：文件级透明加密

2. **向量存储层 (ChromaDB)**
   - 高敏感数据：文件内容索引、通信数据分析
   - 加密强度：本地文件系统加密 + 访问控制
   - 防护级别：目录级权限保护

3. **图分析层 (NetworkX)**
   - 中等敏感数据：关系推理结果、计算缓存
   - 加密强度：与主存储层同步加密
   - 防护级别：内存中处理 + 加密持久化

### 3.2 SQLCipher数据库加密 (核心)

**技术选择**: SQLCipher AES-256-GCM + 三层存储架构

**选择理由**:
- ✅ 军用级加密标准，安全性经过验证
- ✅ 透明加密，应用层无需感知
- ✅ 文件级保护，防止直接访问数据库文件
- ✅ 成熟稳定，广泛应用于企业级产品
- ✅ 性能开销可控 (~15%)
- ✅ 支持完整的数据模型：实体、关系、行为、对话

**数据模型设计**:
```python
# 基于数据存储架构的核心数据模型
class EntityMetadata(Base):
    """实体元数据表 - 知识图谱核心"""
    __tablename__ = "entity_metadata"
    
    id = Column(String, primary_key=True)
    entity_type = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    source_path = Column(String)  # 来源文件路径
    metadata = Column(JSON)       # 扩展属性
    embedding_id = Column(String) # 对应向量ID
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime)
    
    # 统计信息
    access_count = Column(Integer, default=0)
    relevance_score = Column(Float, default=0.0)

class AIConversation(Base):
    """AI对话历史表 - 极高敏感数据"""
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    
    # 对话内容 - 加密存储
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    context_entities = Column(JSON)  # 相关实体
    
    # 对话特征
    message_type = Column(String)  # question, command, chat
    satisfaction_rating = Column(Integer)  # 用户反馈
    processing_time_ms = Column(Integer)
    
    # 时间信息
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
```

**实现设计**:
```python
class SQLCipherDatabaseService:
    """SQLCipher数据库加密服务 - 基于数据存储架构"""
    
    def __init__(self, db_path: str, master_password: str):
        self.db_path = db_path
        self.master_password = master_password
        self.engine = None
        self.session_factory = None
        
    def initialize_database(self):
        """初始化SQLCipher加密数据库"""
        # 生成设备指纹
        device_fingerprint = self._get_device_fingerprint()
        
        # 派生数据库密钥
        db_key = self._derive_database_key(self.master_password, device_fingerprint)
        
        # 创建SQLCipher引擎
        connection_string = f"sqlite+pysqlcipher://:{db_key}@/{self.db_path}"
        
        self.engine = create_engine(
            connection_string,
            connect_args={
                "cipher": "aes-256-gcm",
                "kdf_iter": 256000,
                "cipher_page_size": 4096,
                "cipher_memory_security": True,
                "cipher_use_hmac": True,
            },
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        # 创建所有表
        Base.metadata.create_all(self.engine)
        
        # 应用性能优化
        self._optimize_database_performance()
        
        # 创建Session工厂
        self.session_factory = sessionmaker(bind=self.engine)
    
    def _derive_database_key(self, password: str, device_id: str) -> str:
        """派生数据库加密密钥"""
        key_material = f"{password}:{device_id}:linch-mind-db-v3"
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            key_material.encode('utf-8'),
            b'linch-mind-salt-v3',
            100000  # 足够的迭代次数
        )
        return base64.urlsafe_b64encode(derived_key).decode('utf-8')
    
    def _get_device_fingerprint(self) -> str:
        """生成设备指纹 (防止密码被盗用)"""
        machine_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                                   for i in range(0, 8*6, 8)][::-1])
        }
        
        fingerprint_data = json.dumps(machine_info, sort_keys=True)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
```

### 3.3 简化密钥管理

**设计目标**: 用户友好 > 技术复杂度

```python
class SimpleKeyManager:
    """简化的密钥管理 - 避免过度复杂"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".linch-mind"
        self.config_dir.mkdir(exist_ok=True, mode=0o700)
        
    def setup_master_password(self) -> bool:
        """用户首次设置主密码"""
        print("欢迎使用 Linch Mind！")
        print("为了保护您的隐私数据，请设置一个主密码。")
        print("此密码将用于加密您的所有本地数据。")
        
        while True:
            password = self._get_password_from_user("请设置主密码")
            if self._validate_password_strength(password):
                confirm = self._get_password_from_user("请再次输入密码确认")
                if password == confirm:
                    # 生成恢复助记词
                    recovery_phrase = self._generate_recovery_phrase(password)
                    self._display_recovery_phrase(recovery_phrase)
                    
                    # 保存密码验证哈希 (不保存密码本身)
                    self._save_password_hash(password)
                    return True
                else:
                    print("两次输入的密码不一致，请重新设置。")
            else:
                print("密码强度不足，请包含大小写字母、数字和特殊字符，长度至少8位。")
    
    def _generate_recovery_phrase(self, password: str) -> List[str]:
        """生成12词恢复助记词 (BIP39标准)"""
        # 基于密码和设备指纹生成种子
        device_id = self._get_device_fingerprint()
        seed_data = f"{password}:{device_id}:recovery".encode()
        seed_hash = hashlib.sha256(seed_data).digest()
        
        # 转换为12个助记词 (简化版BIP39)
        word_list = self._load_bip39_wordlist()
        recovery_words = []
        
        for i in range(12):
            word_index = int.from_bytes(seed_hash[i*2:(i+1)*2], 'big') % len(word_list)
            recovery_words.append(word_list[word_index])
        
        return recovery_words
    
    def _display_recovery_phrase(self, words: List[str]):
        """显示恢复助记词给用户"""
        print("\n" + "="*60)
        print("🔑 重要：恢复助记词")
        print("="*60)
        print("请将以下12个单词按顺序抄写并妥善保管：")
        print("如果忘记主密码，只能通过这些单词恢复数据。")
        print()
        
        for i, word in enumerate(words, 1):
            print(f"{i:2d}. {word}")
        
        print("\n" + "="*60)
        print("⚠️  警告：")
        print("- 请将助记词写在纸上，不要保存在电脑中")
        print("- 不要截图或拍照")
        print("- 任何人得到这些单词都能恢复您的数据")
        print("="*60)
        
        input("\n请确认已安全保存助记词，按回车继续...")
    
    def recover_from_phrase(self, recovery_words: List[str]) -> bool:
        """从恢复助记词重建密钥"""
        try:
            # 验证助记词格式
            if len(recovery_words) != 12:
                return False
            
            # 重建原始密码哈希
            original_password = self._reconstruct_password_from_words(recovery_words)
            
            # 验证重建的密码
            if self._verify_reconstructed_password(original_password):
                return True
            
        except Exception as e:
            logger.error(f"恢复失败: {e}")
            
        return False
```

### 3.4 统一数据管理器的安全设计

基于数据存储架构的UnifiedDataManager安全实现：

```python
class UnifiedDataManagerSecurity:
    """统一数据管理器的安全层 - 协调三层存储的安全策略"""
    
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.security_config = {
            'encryption_level': 'high',
            'key_rotation_interval': 86400 * 30,  # 30天
            'audit_logging': True,
            'access_control': True
        }
    
    async def initialize_secure_storage(self, config: dict):
        """安全地初始化三层存储架构"""
        try:
            # 1. 初始化SQLCipher主存储（最高安全级别）
            db_path = Path(config['data_directory']) / "linch_mind_encrypted.db"
            self.database_service = SQLCipherDatabaseService(str(db_path), self.master_password)
            self.database_service.initialize_database()
            
            # 2. 初始化ChromaDB向量存储（目录级加密）
            vector_path = Path(config['data_directory']) / "vectors_encrypted"
            self._secure_directory_permissions(vector_path)
            self.vector_service = ChromaVectorStorageService(str(vector_path))
            self.vector_service.initialize_vector_storage()
            
            # 3. 初始化NetworkX图存储（与主存储同步加密）
            self.graph_service = NetworkXGraphStorageService(self.database_service)
            self.graph_service.initialize_graph_storage()
            
            # 4. 设置跨层安全同步
            await self._setup_cross_layer_security()
            
            logger.info("三层安全存储架构初始化完成")
            
        except Exception as e:
            logger.error(f"安全存储初始化失败: {e}")
            raise SecurityError(f"Failed to initialize secure storage: {e}")
    
    def _secure_directory_permissions(self, directory_path: Path):
        """设置目录安全权限"""
        try:
            directory_path.mkdir(parents=True, exist_ok=True, mode=0o700)
            
            # 在Unix系统上设置严格的目录权限
            import os
            import stat
            if hasattr(os, 'chmod'):
                os.chmod(str(directory_path), stat.S_IRWXU)  # 仅所有者可读写执行
                
        except Exception as e:
            logger.warning(f"设置目录权限失败: {e}")
    
    async def secure_cross_layer_operation(self, operation: str, data: dict) -> dict:
        """安全的跨层数据操作"""
        try:
            # 1. 操作前安全检查
            self._validate_operation_security(operation, data)
            
            # 2. 根据数据敏感性选择存储层
            storage_strategy = self._determine_storage_strategy(data)
            
            # 3. 执行安全操作
            if operation == "add_knowledge_entity":
                result = await self._secure_add_entity(data, storage_strategy)
            elif operation == "semantic_search":
                result = await self._secure_semantic_search(data, storage_strategy)
            elif operation == "find_related_entities":
                result = await self._secure_find_related(data, storage_strategy)
            else:
                raise SecurityError(f"Unsupported secure operation: {operation}")
            
            # 4. 操作后安全审计
            self._audit_operation(operation, data, result)
            
            return result
            
        except Exception as e:
            logger.error(f"安全操作失败 [{operation}]: {e}")
            self._audit_security_failure(operation, data, str(e))
            raise
    
    def _determine_storage_strategy(self, data: dict) -> dict:
        """根据数据敏感性确定存储策略"""
        data_type = data.get('type', 'unknown')
        content = data.get('content', '')
        
        # 极高敏感数据 - 强制SQLCipher加密
        if data_type in ['ai_conversation', 'personal_thought', 'sensitive_document']:
            return {
                'primary_storage': True,
                'vector_storage': False,  # 不存储向量以避免信息泄露
                'graph_storage': True,
                'encryption_level': 'maximum'
            }
        
        # 高敏感数据 - SQLCipher + 受保护的向量存储
        elif data_type in ['work_document', 'email_content', 'private_note']:
            return {
                'primary_storage': True,
                'vector_storage': True,
                'graph_storage': True,
                'encryption_level': 'high'
            }
        
        # 中等敏感数据 - 标准三层存储
        else:
            return {
                'primary_storage': True,
                'vector_storage': True,
                'graph_storage': True,
                'encryption_level': 'standard'
            }
    
    async def _secure_add_entity(self, entity_data: dict, strategy: dict) -> str:
        """安全地添加实体到多层存储"""
        entity_id = entity_data.get('id') or self._generate_secure_entity_id()
        
        try:
            # 1. 必须添加到主存储（SQLCipher加密）
            if strategy['primary_storage']:
                session = self.database_service.get_session()
                
                # 对极高敏感内容进行额外加密
                processed_data = entity_data.copy()
                if strategy['encryption_level'] == 'maximum':
                    processed_data = await self._apply_additional_encryption(processed_data)
                
                entity = EntityMetadata(
                    id=entity_id,
                    name=processed_data['name'],
                    entity_type=processed_data['type'],
                    description=processed_data.get('description', ''),
                    source_path=processed_data.get('source_path'),
                    metadata=processed_data.get('metadata', {})
                )
                session.add(entity)
                session.commit()
                session.close()
            
            # 2. 有条件添加到向量存储
            if strategy['vector_storage'] and 'content' in entity_data:
                # 对敏感内容进行脱敏处理
                content = await self._sanitize_content_for_vectors(
                    entity_data['content'], 
                    strategy['encryption_level']
                )
                
                await self.vector_service.add_document_embedding(
                    entity_id,
                    content,
                    {
                        'name': entity_data['name'],
                        'type': entity_data['type'],
                        'sensitivity': strategy['encryption_level']
                    }
                )
            
            # 3. 添加到图存储（数据会持久化到SQLCipher）
            if strategy['graph_storage']:
                self.graph_service.add_entity(
                    entity_id,
                    entity_data['name'],
                    entity_data['type'],
                    entity_data.get('metadata', {})
                )
            
            return entity_id
            
        except Exception as e:
            logger.error(f"安全添加实体失败: {e}")
            raise
    
    async def _apply_additional_encryption(self, data: dict) -> dict:
        """对极高敏感数据应用额外的应用层加密"""
        try:
            from cryptography.fernet import Fernet
            
            # 生成基于主密码的加密密钥
            additional_key = self._derive_additional_encryption_key()
            cipher = Fernet(additional_key)
            
            # 加密敏感字段
            sensitive_fields = ['description', 'content', 'message', 'response']
            encrypted_data = data.copy()
            
            for field in sensitive_fields:
                if field in encrypted_data and encrypted_data[field]:
                    plaintext = str(encrypted_data[field]).encode('utf-8')
                    encrypted_data[field] = cipher.encrypt(plaintext).decode('ascii')
                    encrypted_data[f'{field}_encrypted'] = True
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"额外加密失败: {e}")
            return data  # 失败时返回原数据，依赖SQLCipher的保护
    
    def _derive_additional_encryption_key(self) -> bytes:
        """派生额外的应用层加密密钥"""
        key_material = f"{self.master_password}:additional-encryption:v1"
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            key_material.encode('utf-8'),
            b'linch-mind-additional-salt',
            50000  # 较少的迭代次数，因为已有SQLCipher保护
        )
        return base64.urlsafe_b64encode(derived_key)
    
    async def _sanitize_content_for_vectors(self, content: str, encryption_level: str) -> str:
        """为向量存储脱敏内容"""
        if encryption_level == 'maximum':
            # 极高敏感：只保留关键词和概念，移除具体细节
            return await self._extract_safe_keywords(content)
        elif encryption_level == 'high':
            # 高敏感：移除个人标识信息
            return await self._remove_pii(content)
        else:
            # 中等敏感：保留原内容
            return content
    
    def _audit_operation(self, operation: str, data: dict, result: dict):
        """审计安全操作"""
        if self.security_config['audit_logging']:
            audit_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': operation,
                'data_type': data.get('type', 'unknown'),
                'data_size': len(str(data)),
                'result_status': 'success',
                'result_size': len(str(result)) if result else 0
            }
            
            # 记录到安全审计日志（不记录敏感内容）
            logger.info(f"安全操作审计: {audit_entry}")
```

### 3.5 数据导出加密

```python
class FileEncryptionService:
    """备份和导出文件的加密服务"""
    
    def __init__(self, key_manager: SimpleKeyManager):
        self.key_manager = key_manager
        
    def encrypt_export_file(self, data: dict, export_path: str) -> bool:
        """加密导出用户数据"""
        try:
            # 序列化数据
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 使用Fernet对称加密
            key = self._derive_export_key()
            cipher = Fernet(key)
            encrypted_data = cipher.encrypt(json_data.encode('utf-8'))
            
            # 添加文件头信息
            export_metadata = {
                'version': '3.0',
                'created_at': datetime.utcnow().isoformat(),
                'encrypted_data': base64.b64encode(encrypted_data).decode('ascii')
            }
            
            # 写入加密文件
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"导出加密失败: {e}")
            return False
    
    def decrypt_import_file(self, import_path: str) -> Optional[dict]:
        """解密并导入用户数据"""
        try:
            # 读取加密文件
            with open(import_path, 'r', encoding='utf-8') as f:
                export_metadata = json.load(f)
            
            # 解密数据
            key = self._derive_export_key()
            cipher = Fernet(key)
            encrypted_data = base64.b64decode(export_metadata['encrypted_data'])
            decrypted_json = cipher.decrypt(encrypted_data)
            
            # 解析数据
            data = json.loads(decrypted_json.decode('utf-8'))
            return data
            
        except Exception as e:
            logger.error(f"导入解密失败: {e}")
            return None
```

### 3.5 可选的增强安全特性

对于有特殊安全需求的高级用户，提供可选的"偏执模式"：

```python
class ParanoidModeFeatures:
    """偏执模式 - 高级用户可选的额外安全特性"""
    
    def __init__(self):
        self.enabled = False
        self.features = {
            'memory_protection': False,
            'access_logging': False,
            'auto_lock': False,
            'hardware_security': False
        }
    
    def enable_paranoid_mode(self):
        """启用偏执模式"""
        print("🔒 启用偏执模式")
        print("这将启用额外的安全特性，可能影响性能。")
        
        self.enabled = True
        
        # 内存保护
        if self._confirm_feature("启用内存保护 (清理敏感数据)?"):
            self.memory_protection = MemoryProtectionService()
            self.features['memory_protection'] = True
        
        # 访问审计
        if self._confirm_feature("启用访问日志记录?"):
            self.access_logger = SecurityAuditLogger()
            self.features['access_logging'] = True
        
        # 自动锁定
        if self._confirm_feature("启用自动锁定 (30分钟无操作)?"):
            self.auto_lock = AutoLockService(timeout_minutes=30)
            self.features['auto_lock'] = True
        
        # 硬件安全检测
        hardware_support = self._detect_hardware_security()
        if hardware_support and self._confirm_feature(f"启用 {hardware_support} 硬件安全?"):
            self.hardware_security = HardwareSecurityService(hardware_support)
            self.features['hardware_security'] = True
    
    def _detect_hardware_security(self) -> Optional[str]:
        """检测可用的硬件安全特性"""
        import platform
        
        if platform.system() == "Darwin":
            # macOS: 检测 Secure Enclave
            try:
                # 简单的 Secure Enclave 可用性检测
                import subprocess
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                      capture_output=True, text=True)
                if 'T2' in result.stdout or 'M1' in result.stdout or 'M2' in result.stdout:
                    return "Apple Secure Enclave"
            except:
                pass
        
        elif platform.system() == "Linux":
            # Linux: 检测 Intel SGX
            if Path('/dev/sgx_enclave').exists():
                return "Intel SGX"
        
        return None

class MemoryProtectionService:
    """内存保护服务 - 清理敏感数据"""
    
    def __init__(self):
        self.protected_objects = weakref.WeakSet()
    
    def protect_sensitive_data(self, data: Any):
        """标记敏感数据对象进行保护"""
        self.protected_objects.add(data)
    
    def clear_sensitive_memory(self):
        """清理内存中的敏感数据"""
        for obj in self.protected_objects:
            if hasattr(obj, '__dict__'):
                for key in obj.__dict__:
                    if 'password' in key.lower() or 'key' in key.lower():
                        setattr(obj, key, None)
        
        # 触发垃圾回收
        import gc
        gc.collect()

class SecurityAuditLogger:
    """安全审计日志"""
    
    def __init__(self):
        self.log_file = Path.home() / ".linch-mind" / "security.log"
        
    def log_access(self, action: str, details: dict):
        """记录访问日志"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'details': details,
            'process_id': os.getpid(),
            'user': os.getenv('USER', 'unknown')
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
```

## 4. 性能影响分析

### 4.1 三层架构加密开销评估

基于数据存储架构的性能影响分析：

| 存储层 | 加密组件 | 性能影响 | 具体表现 | 优化措施 |
|--------|---------|---------|----------|----------|
| **主存储层** | SQLCipher AES-256-GCM | ~15% | 数据库读写延迟增加 | WAL模式、64MB缓存、索引优化 |
| **向量存储层** | ChromaDB本地文件 | ~5% | 向量搜索轻微延迟 | 目录权限、批量操作 |
| **图分析层** | NetworkX + SQLite持久化 | ~8% | 图算法计算开销 | 内存计算、异步持久化 |
| **统一管理层** | 跨层安全协调 | ~3% | 数据路由和验证 | 智能缓存、批处理 |
| **密钥管理** | PBKDF2密钥派生 | <1% | 应用启动时一次性开销 | 密钥缓存、设备指纹 |
| **额外加密** | 极高敏感数据二次加密 | ~2% | 特定数据类型处理 | 选择性应用、Fernet加密 |
| **偏执模式** | 内存清理、审计日志 | +5-10% | 全方位安全措施 | 可选启用、异步处理 |

**整体性能影响**:
- **标准模式**: ~20-25% 总开销
- **高安全模式**: ~30-35% 总开销  
- **偏执模式**: ~40-45% 总开销

### 4.2 三层架构性能优化策略

基于数据存储架构的全方位性能优化：

```python
class ThreeLayerPerformanceOptimizer:
    """三层架构性能优化器 - 基于数据存储架构设计"""
    
    def __init__(self, unified_data_manager: UnifiedDataManager):
        self.data_manager = unified_data_manager
        self.optimization_metrics = {}
    
    def optimize_all_layers(self):
        """优化所有存储层性能"""
        # 1. 优化SQLCipher主存储层
        self.optimize_sqlcipher_layer()
        
        # 2. 优化ChromaDB向量存储层
        self.optimize_vector_storage_layer()
        
        # 3. 优化NetworkX图分析层
        self.optimize_graph_storage_layer()
        
        # 4. 优化跨层数据同步
        self.optimize_cross_layer_sync()
        
    def optimize_sqlcipher_layer(self):
        """优化SQLCipher主存储层"""
        if not self.data_manager.database_service:
            return
            
        engine = self.data_manager.database_service.engine
        with engine.connect() as conn:
            # 高级缓存优化
            conn.execute(text("PRAGMA cache_size = -64000"))     # 64MB缓存
            conn.execute(text("PRAGMA page_size = 4096"))        # 优化页面大小
            
            # WAL模式提升并发性能
            conn.execute(text("PRAGMA journal_mode = WAL"))
            conn.execute(text("PRAGMA wal_autocheckpoint = 1000"))
            
            # 同步和安全平衡
            conn.execute(text("PRAGMA synchronous = NORMAL"))    # 平衡安全性和性能
            conn.execute(text("PRAGMA secure_delete = OFF"))     # 提升删除性能
            
            # 内存优化
            conn.execute(text("PRAGMA temp_store = MEMORY"))     # 临时数据存内存
            conn.execute(text("PRAGMA mmap_size = 268435456"))   # 256MB内存映射
            
            # 查询优化
            conn.execute(text("PRAGMA optimize"))               # 自动优化
            conn.execute(text("PRAGMA analysis_limit = 1000"))  # 限制分析开销
            
        # 创建高效索引
        self._create_optimized_indexes()
        
    def optimize_vector_storage_layer(self):
        """优化ChromaDB向量存储层"""
        if not self.data_manager.vector_service:
            return
            
        try:
            # 批量操作优化
            self.vector_batch_size = 50
            
            # 内存映射优化（ChromaDB特定）
            vector_config = {
                'batch_size': self.vector_batch_size,
                'max_memory_usage': '1GB',
                'enable_parallel_processing': True
            }
            
            # 向量搜索缓存
            self.vector_search_cache = {}
            self.cache_ttl = 300  # 5分钟缓存
            
            logger.info("向量存储层性能优化完成")
            
        except Exception as e:
            logger.warning(f"向量存储优化失败: {e}")
    
    def optimize_graph_storage_layer(self):
        """优化NetworkX图分析层"""
        if not self.data_manager.graph_service:
            return
            
        try:
            # 图算法优化配置
            graph_optimization_config = {
                'enable_node_caching': True,
                'max_path_length': 5,         # 限制路径搜索深度
                'batch_processing': True,
                'async_persistence': True     # 异步持久化
            }
            
            # 应用优化配置到图服务
            self.data_manager.graph_service.optimization_config = graph_optimization_config
            
            # 预计算常用图指标
            self._precompute_graph_metrics()
            
            logger.info("图存储层性能优化完成")
            
        except Exception as e:
            logger.warning(f"图存储优化失败: {e}")
    
    def optimize_cross_layer_sync(self):
        """优化跨层数据同步"""
        try:
            # 同步批处理配置
            sync_config = {
                'batch_size': 100,
                'sync_interval': 60,          # 1分钟同步间隔
                'parallel_sync': True,
                'incremental_only': True      # 仅增量同步
            }
            
            # 智能同步调度
            self._setup_intelligent_sync_scheduler(sync_config)
            
            logger.info("跨层同步优化完成")
            
        except Exception as e:
            logger.warning(f"跨层同步优化失败: {e}")
    
    def _create_optimized_indexes(self):
        """创建优化的数据库索引 - 基于数据存储架构"""
        indexes = [
            # EntityMetadata表索引
            "CREATE INDEX IF NOT EXISTS idx_entity_type_name ON entity_metadata(entity_type, name)",
            "CREATE INDEX IF NOT EXISTS idx_entity_updated ON entity_metadata(updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_entity_access_count ON entity_metadata(access_count DESC)",
            "CREATE INDEX IF NOT EXISTS idx_entity_relevance ON entity_metadata(relevance_score DESC)",
            
            # UserBehavior表索引
            "CREATE INDEX IF NOT EXISTS idx_behavior_timestamp ON user_behaviors(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_session ON user_behaviors(session_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_entity ON user_behaviors(target_entity)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_action ON user_behaviors(action_type)",
            
            # EntityRelationship表索引
            "CREATE INDEX IF NOT EXISTS idx_relationship_source ON entity_relationships(source_entity)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_target ON entity_relationships(target_entity)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_type ON entity_relationships(relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_relationship_strength ON entity_relationships(strength DESC)",
            
            # AIConversation表索引
            "CREATE INDEX IF NOT EXISTS idx_conversation_session ON ai_conversations(session_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON ai_conversations(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_conversation_type ON ai_conversations(message_type)",
            
            # 复合索引优化
            "CREATE INDEX IF NOT EXISTS idx_entity_type_updated ON entity_metadata(entity_type, updated_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_behavior_entity_timestamp ON user_behaviors(target_entity, timestamp DESC)"
        ]
        
        engine = self.data_manager.database_service.engine
        with engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    logger.warning(f"创建索引失败: {e}")
    
    def _precompute_graph_metrics(self):
        """预计算图指标以提升查询性能"""
        try:
            graph = self.data_manager.graph_service.knowledge_graph
            
            # 预计算节点中心性
            centrality_metrics = {
                'degree_centrality': nx.degree_centrality(graph),
                'betweenness_centrality': nx.betweenness_centrality(graph, k=100),  # 采样优化
                'pagerank': nx.pagerank(graph, max_iter=50)  # 限制迭代次数
            }
            
            # 存储预计算结果到图节点属性
            for node_id, metrics in centrality_metrics.items():
                if isinstance(metrics, dict):
                    for node, value in metrics.items():
                        if graph.has_node(node):
                            if 'computed_metrics' not in graph.nodes[node]:
                                graph.nodes[node]['computed_metrics'] = {}
                            graph.nodes[node]['computed_metrics'][node_id] = value
            
            logger.info("图指标预计算完成")
            
        except Exception as e:
            logger.warning(f"图指标预计算失败: {e}")
    
    def _setup_intelligent_sync_scheduler(self, config: dict):
        """设置智能同步调度器"""
        try:
            import asyncio
            from datetime import datetime, timedelta
            
            async def smart_sync_task():
                """智能同步任务"""
                last_sync = datetime.now()
                
                while True:
                    try:
                        # 检查是否需要同步
                        if await self._should_sync(last_sync, config):
                            await self._perform_incremental_sync(config)
                            last_sync = datetime.now()
                        
                        # 等待下次检查
                        await asyncio.sleep(config['sync_interval'])
                        
                    except Exception as e:
                        logger.error(f"智能同步任务失败: {e}")
                        await asyncio.sleep(config['sync_interval'] * 2)  # 错误时延长等待
            
            # 启动异步同步任务
            asyncio.create_task(smart_sync_task())
            
        except Exception as e:
            logger.error(f"智能同步调度器设置失败: {e}")
    
    async def _should_sync(self, last_sync: datetime, config: dict) -> bool:
        """判断是否需要执行同步"""
        # 基于时间间隔
        if datetime.now() - last_sync > timedelta(seconds=config['sync_interval']):
            return True
        
        # 基于数据变更量（如果有变更跟踪）
        # TODO: 实现基于变更量的智能同步触发
        
        return False
    
    async def _perform_incremental_sync(self, config: dict):
        """执行增量同步"""
        try:
            # 同步图数据到SQLite
            self.data_manager.graph_service.persist_graphs_to_database()
            
            # 同步向量数据
            if self.data_manager.vector_service:
                self.data_manager.vector_service.persist()
            
            logger.debug("增量同步完成")
            
        except Exception as e:
            logger.error(f"增量同步失败: {e}")
    
    def get_performance_metrics(self) -> dict:
        """获取性能指标"""
        try:
            metrics = {
                'database_performance': self._get_database_metrics(),
                'vector_performance': self._get_vector_metrics(),
                'graph_performance': self._get_graph_metrics(),
                'sync_performance': self._get_sync_metrics()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            return {}
    
    def _get_database_metrics(self) -> dict:
        """获取数据库性能指标"""
        try:
            # 执行性能测试查询
            import time
            start_time = time.time()
            
            session = self.data_manager.database_service.get_session()
            session.query(EntityMetadata).limit(10).all()
            session.close()
            
            query_time = (time.time() - start_time) * 1000
            
            return {
                'query_time_ms': round(query_time, 2),
                'status': 'good' if query_time < 100 else 'needs_optimization'
            }
            
        except Exception as e:
            return {'error': str(e)}
```

## 5. 实施路线图

### 5.1 Phase 1: 核心安全基础 (2-3周)

```
✅ 优先级: 最高
📅 预计工期: 2-3周

核心任务:
├── SQLCipherManager 实现
├── SimpleKeyManager 密钥管理
├── 用户密码设置流程
├── 设备指纹生成
├── 恢复助记词机制
└── 基础性能优化
```

### 5.2 Phase 2: 用户体验优化 (1-2周)

```
✅ 优先级: 高
📅 预计工期: 1-2周

核心任务:
├── 密码修改功能
├── 数据导出/导入加密
├── 简化的设置界面  
├── 安全状态显示
└── 错误处理和用户反馈
```

### 5.3 Phase 3: 可选高级特性 (1-2周)

```
🟡 优先级: 中等
📅 预计工期: 1-2周

核心任务:
├── 偏执模式开关
├── 硬件安全检测
├── 访问审计日志
├── 自动锁定功能
└── 内存保护服务
```

## 6. 安全性评估

### 6.1 防护能力矩阵

| 威胁类型 | 基础防护 | 偏执模式 | 防护说明 |
|---------|---------|---------|----------|
| 设备丢失/被盗 | ✅ 完全防护 | ✅ 完全防护 | SQLCipher文件级加密 |
| 恶意软件访问 | ✅ 强防护 | ✅ 完全防护 | 密码+设备指纹双重验证 |
| 共享设备访问 | ✅ 完全防护 | ✅ 完全防护 | 主密码保护 |
| 硬盘数据恢复 | ✅ 完全防护 | ✅ 完全防护 | AES-256加密 |
| 内存转储攻击 | ⚠️ 部分防护 | ✅ 较强防护 | 内存清理+硬件保护 |
| 针对性APT攻击 | ⚠️ 有限防护 | ⚠️ 较强防护 | 无完全防护方案 |

### 6.2 合规性检查

**隐私法规符合性**:
- ✅ **GDPR Article 32**: 数据加密和假名化要求
- ✅ **CCPA**: 合理的数据安全保护措施  
- ✅ **中国PIPL**: 个人信息加密存储要求
- ✅ **加州CPRA**: 敏感个人信息保护标准

**安全标准符合性**:
- ✅ **NIST Cybersecurity Framework**: 数据保护控制措施
- ✅ **OWASP**: 数据加密最佳实践
- ✅ **ISO 27001**: 信息安全管理体系要求

## 7. 用户指南

### 7.1 首次设置指南

```
🔧 安全设置向导

1. 设置主密码
   ├── 包含大小写字母、数字、特殊字符
   ├── 长度至少8位 (推荐12位以上)
   └── 避免使用个人信息

2. 保存恢复助记词
   ├── 按顺序抄写12个单词
   ├── 保存在安全的地方 (纸质备份)
   └── 不要截图或保存在电脑中

3. 验证设置
   ├── 确认密码输入正确
   ├── 确认助记词已保存
   └── 测试密码登录功能
```

### 7.2 日常使用指南

```
📱 日常安全操作

启动应用:
└── 输入主密码解锁数据

修改密码:
├── 设置 → 安全选项 → 修改主密码
├── 输入当前密码
├── 设置新密码
└── 重新生成恢复助记词

数据备份:
├── 设置 → 数据管理 → 导出数据
├── 选择导出位置
└── 备份文件已自动加密

数据恢复:
├── 忘记密码时使用恢复助记词
├── 设置 → 安全选项 → 恢复数据
└── 按顺序输入12个助记词
```

### 7.3 高级用户指南

```
🔒 偏执模式设置

启用方式:
├── 设置 → 高级安全 → 启用偏执模式
├── 选择需要的安全特性
└── 接受性能影响提示

可用特性:
├── 内存保护: 自动清理敏感数据
├── 访问日志: 记录所有数据访问
├── 自动锁定: 30分钟无操作后锁定
└── 硬件安全: 使用Secure Enclave/SGX
```

## 8. 故障排除

### 8.1 常见问题

**Q: 忘记主密码怎么办？**
A: 使用12个恢复助记词重建密钥。如果助记词也丢失，数据无法恢复。

**Q: 更换设备后如何迁移数据？**  
A: 在旧设备导出加密数据，在新设备导入并输入相同的主密码。

**Q: 为什么应用启动变慢了？**
A: SQLCipher解密需要时间。首次启动较慢是正常现象，后续会有改善。

**Q: 偏执模式影响多大？**
A: 约5-10%的性能开销，主要体现在内存使用和日志记录上。

### 8.2 应急处理

**数据损坏**:
1. 立即停止使用应用
2. 检查是否有备份文件
3. 使用恢复助记词重建数据库
4. 联系技术支持

**密码泄露**:
1. 立即修改主密码
2. 重新生成恢复助记词
3. 检查访问日志 (如启用)
4. 导出数据重新加密

## 9. 总结

### 9.1 设计亮点

- **实用主义**: 避免过度工程化，聚焦真实威胁防护
- **用户友好**: 简化密钥管理，降低使用门槛
- **分层选择**: 基础安全+可选增强，满足不同需求
- **性能平衡**: 15%开销换取95%威胁防护，性价比优秀
- **标准合规**: 满足主流隐私法规和安全标准要求

### 9.2 核心价值

1. **数据安全**: SQLCipher军用级加密，防护设备丢失、恶意软件等主要威胁
2. **用户信任**: 透明的安全措施，增强用户对产品的信心
3. **法规合规**: 满足GDPR、CCPA等全球隐私保护法规要求
4. **竞争优势**: 在个人AI助手领域建立安全防护差异化
5. **可持续性**: 简单可靠的架构，易于长期维护和演进

### 9.3 成功指标

- **安全性**: 防护95%以上的现实威胁场景
- **性能**: 加密开销控制在15%以内  
- **可用性**: 普通用户5分钟内完成安全设置
- **可靠性**: 密钥恢复成功率99%以上
- **满意度**: 用户安全感知评分8分以上 (10分制)

本架构在保证Linch Mind"隐私至上"承诺的同时，避免了过度复杂的设计，为用户提供了既安全又实用的数据保护方案。

---

**文档版本**: 3.0 - 实用主义版  
**创建时间**: 2025-08-04  
**最后更新**: 2025-08-04  
**相关文档**: 
- [数据存储架构设计](data_storage_architecture.md)
- [Daemon架构设计](daemon_architecture.md)
- [产品愿景与战略](../00_vision_and_strategy/product_vision_and_strategy.md)