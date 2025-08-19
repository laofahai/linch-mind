// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'mode_switch_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$ModeSwitchState {
  AppMode get currentMode => throw _privateConstructorUsedError;
  bool get isTransitioning => throw _privateConstructorUsedError;
  DateTime? get lastSwitchTime => throw _privateConstructorUsedError;
  Map<AppMode, DateTime>? get modeUsageStats =>
      throw _privateConstructorUsedError;

  /// Create a copy of ModeSwitchState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ModeSwitchStateCopyWith<ModeSwitchState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ModeSwitchStateCopyWith<$Res> {
  factory $ModeSwitchStateCopyWith(
          ModeSwitchState value, $Res Function(ModeSwitchState) then) =
      _$ModeSwitchStateCopyWithImpl<$Res, ModeSwitchState>;
  @useResult
  $Res call(
      {AppMode currentMode,
      bool isTransitioning,
      DateTime? lastSwitchTime,
      Map<AppMode, DateTime>? modeUsageStats});
}

/// @nodoc
class _$ModeSwitchStateCopyWithImpl<$Res, $Val extends ModeSwitchState>
    implements $ModeSwitchStateCopyWith<$Res> {
  _$ModeSwitchStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ModeSwitchState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentMode = null,
    Object? isTransitioning = null,
    Object? lastSwitchTime = freezed,
    Object? modeUsageStats = freezed,
  }) {
    return _then(_value.copyWith(
      currentMode: null == currentMode
          ? _value.currentMode
          : currentMode // ignore: cast_nullable_to_non_nullable
              as AppMode,
      isTransitioning: null == isTransitioning
          ? _value.isTransitioning
          : isTransitioning // ignore: cast_nullable_to_non_nullable
              as bool,
      lastSwitchTime: freezed == lastSwitchTime
          ? _value.lastSwitchTime
          : lastSwitchTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      modeUsageStats: freezed == modeUsageStats
          ? _value.modeUsageStats
          : modeUsageStats // ignore: cast_nullable_to_non_nullable
              as Map<AppMode, DateTime>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ModeSwitchStateImplCopyWith<$Res>
    implements $ModeSwitchStateCopyWith<$Res> {
  factory _$$ModeSwitchStateImplCopyWith(_$ModeSwitchStateImpl value,
          $Res Function(_$ModeSwitchStateImpl) then) =
      __$$ModeSwitchStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {AppMode currentMode,
      bool isTransitioning,
      DateTime? lastSwitchTime,
      Map<AppMode, DateTime>? modeUsageStats});
}

/// @nodoc
class __$$ModeSwitchStateImplCopyWithImpl<$Res>
    extends _$ModeSwitchStateCopyWithImpl<$Res, _$ModeSwitchStateImpl>
    implements _$$ModeSwitchStateImplCopyWith<$Res> {
  __$$ModeSwitchStateImplCopyWithImpl(
      _$ModeSwitchStateImpl _value, $Res Function(_$ModeSwitchStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of ModeSwitchState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentMode = null,
    Object? isTransitioning = null,
    Object? lastSwitchTime = freezed,
    Object? modeUsageStats = freezed,
  }) {
    return _then(_$ModeSwitchStateImpl(
      currentMode: null == currentMode
          ? _value.currentMode
          : currentMode // ignore: cast_nullable_to_non_nullable
              as AppMode,
      isTransitioning: null == isTransitioning
          ? _value.isTransitioning
          : isTransitioning // ignore: cast_nullable_to_non_nullable
              as bool,
      lastSwitchTime: freezed == lastSwitchTime
          ? _value.lastSwitchTime
          : lastSwitchTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      modeUsageStats: freezed == modeUsageStats
          ? _value._modeUsageStats
          : modeUsageStats // ignore: cast_nullable_to_non_nullable
              as Map<AppMode, DateTime>?,
    ));
  }
}

/// @nodoc

class _$ModeSwitchStateImpl implements _ModeSwitchState {
  const _$ModeSwitchStateImpl(
      {this.currentMode = AppMode.daily,
      this.isTransitioning = false,
      this.lastSwitchTime,
      final Map<AppMode, DateTime>? modeUsageStats})
      : _modeUsageStats = modeUsageStats;

  @override
  @JsonKey()
  final AppMode currentMode;
  @override
  @JsonKey()
  final bool isTransitioning;
  @override
  final DateTime? lastSwitchTime;
  final Map<AppMode, DateTime>? _modeUsageStats;
  @override
  Map<AppMode, DateTime>? get modeUsageStats {
    final value = _modeUsageStats;
    if (value == null) return null;
    if (_modeUsageStats is EqualUnmodifiableMapView) return _modeUsageStats;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'ModeSwitchState(currentMode: $currentMode, isTransitioning: $isTransitioning, lastSwitchTime: $lastSwitchTime, modeUsageStats: $modeUsageStats)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ModeSwitchStateImpl &&
            (identical(other.currentMode, currentMode) ||
                other.currentMode == currentMode) &&
            (identical(other.isTransitioning, isTransitioning) ||
                other.isTransitioning == isTransitioning) &&
            (identical(other.lastSwitchTime, lastSwitchTime) ||
                other.lastSwitchTime == lastSwitchTime) &&
            const DeepCollectionEquality()
                .equals(other._modeUsageStats, _modeUsageStats));
  }

  @override
  int get hashCode => Object.hash(runtimeType, currentMode, isTransitioning,
      lastSwitchTime, const DeepCollectionEquality().hash(_modeUsageStats));

  /// Create a copy of ModeSwitchState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ModeSwitchStateImplCopyWith<_$ModeSwitchStateImpl> get copyWith =>
      __$$ModeSwitchStateImplCopyWithImpl<_$ModeSwitchStateImpl>(
          this, _$identity);
}

abstract class _ModeSwitchState implements ModeSwitchState {
  const factory _ModeSwitchState(
      {final AppMode currentMode,
      final bool isTransitioning,
      final DateTime? lastSwitchTime,
      final Map<AppMode, DateTime>? modeUsageStats}) = _$ModeSwitchStateImpl;

  @override
  AppMode get currentMode;
  @override
  bool get isTransitioning;
  @override
  DateTime? get lastSwitchTime;
  @override
  Map<AppMode, DateTime>? get modeUsageStats;

  /// Create a copy of ModeSwitchState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ModeSwitchStateImplCopyWith<_$ModeSwitchStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
