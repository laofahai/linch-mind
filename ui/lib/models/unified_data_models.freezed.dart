// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'unified_data_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

UniversalIndexEntry _$UniversalIndexEntryFromJson(Map<String, dynamic> json) {
  return _UniversalIndexEntry.fromJson(json);
}

/// @nodoc
mixin _$UniversalIndexEntry {
  String get id => throw _privateConstructorUsedError;
  String get connectorId => throw _privateConstructorUsedError;
  UniversalContentType get contentType => throw _privateConstructorUsedError;
  String get primaryKey => throw _privateConstructorUsedError;
  String get searchableText => throw _privateConstructorUsedError;
  String get displayName => throw _privateConstructorUsedError;
  IndexTier get indexTier => throw _privateConstructorUsedError;
  int get priority => throw _privateConstructorUsedError;
  DateTime get indexedAt => throw _privateConstructorUsedError;
  DateTime? get lastModified => throw _privateConstructorUsedError;
  DateTime? get lastAccessed => throw _privateConstructorUsedError;
  Map<String, dynamic> get structuredData => throw _privateConstructorUsedError;
  Map<String, dynamic> get metadata => throw _privateConstructorUsedError;
  List<String> get keywords => throw _privateConstructorUsedError;
  List<String> get tags => throw _privateConstructorUsedError; // 搜索相关字段
  double get score => throw _privateConstructorUsedError;
  String? get snippet => throw _privateConstructorUsedError; // 扩展方法需要的字段
  String get title => throw _privateConstructorUsedError;
  String? get summary => throw _privateConstructorUsedError;
  String? get content => throw _privateConstructorUsedError;

  /// Serializes this UniversalIndexEntry to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UniversalIndexEntry
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UniversalIndexEntryCopyWith<UniversalIndexEntry> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UniversalIndexEntryCopyWith<$Res> {
  factory $UniversalIndexEntryCopyWith(
          UniversalIndexEntry value, $Res Function(UniversalIndexEntry) then) =
      _$UniversalIndexEntryCopyWithImpl<$Res, UniversalIndexEntry>;
  @useResult
  $Res call(
      {String id,
      String connectorId,
      UniversalContentType contentType,
      String primaryKey,
      String searchableText,
      String displayName,
      IndexTier indexTier,
      int priority,
      DateTime indexedAt,
      DateTime? lastModified,
      DateTime? lastAccessed,
      Map<String, dynamic> structuredData,
      Map<String, dynamic> metadata,
      List<String> keywords,
      List<String> tags,
      double score,
      String? snippet,
      String title,
      String? summary,
      String? content});
}

/// @nodoc
class _$UniversalIndexEntryCopyWithImpl<$Res, $Val extends UniversalIndexEntry>
    implements $UniversalIndexEntryCopyWith<$Res> {
  _$UniversalIndexEntryCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UniversalIndexEntry
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? connectorId = null,
    Object? contentType = null,
    Object? primaryKey = null,
    Object? searchableText = null,
    Object? displayName = null,
    Object? indexTier = null,
    Object? priority = null,
    Object? indexedAt = null,
    Object? lastModified = freezed,
    Object? lastAccessed = freezed,
    Object? structuredData = null,
    Object? metadata = null,
    Object? keywords = null,
    Object? tags = null,
    Object? score = null,
    Object? snippet = freezed,
    Object? title = null,
    Object? summary = freezed,
    Object? content = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      contentType: null == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as UniversalContentType,
      primaryKey: null == primaryKey
          ? _value.primaryKey
          : primaryKey // ignore: cast_nullable_to_non_nullable
              as String,
      searchableText: null == searchableText
          ? _value.searchableText
          : searchableText // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      indexTier: null == indexTier
          ? _value.indexTier
          : indexTier // ignore: cast_nullable_to_non_nullable
              as IndexTier,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as int,
      indexedAt: null == indexedAt
          ? _value.indexedAt
          : indexedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      lastModified: freezed == lastModified
          ? _value.lastModified
          : lastModified // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastAccessed: freezed == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      structuredData: null == structuredData
          ? _value.structuredData
          : structuredData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      metadata: null == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      keywords: null == keywords
          ? _value.keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>,
      tags: null == tags
          ? _value.tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      score: null == score
          ? _value.score
          : score // ignore: cast_nullable_to_non_nullable
              as double,
      snippet: freezed == snippet
          ? _value.snippet
          : snippet // ignore: cast_nullable_to_non_nullable
              as String?,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      summary: freezed == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String?,
      content: freezed == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UniversalIndexEntryImplCopyWith<$Res>
    implements $UniversalIndexEntryCopyWith<$Res> {
  factory _$$UniversalIndexEntryImplCopyWith(_$UniversalIndexEntryImpl value,
          $Res Function(_$UniversalIndexEntryImpl) then) =
      __$$UniversalIndexEntryImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String connectorId,
      UniversalContentType contentType,
      String primaryKey,
      String searchableText,
      String displayName,
      IndexTier indexTier,
      int priority,
      DateTime indexedAt,
      DateTime? lastModified,
      DateTime? lastAccessed,
      Map<String, dynamic> structuredData,
      Map<String, dynamic> metadata,
      List<String> keywords,
      List<String> tags,
      double score,
      String? snippet,
      String title,
      String? summary,
      String? content});
}

/// @nodoc
class __$$UniversalIndexEntryImplCopyWithImpl<$Res>
    extends _$UniversalIndexEntryCopyWithImpl<$Res, _$UniversalIndexEntryImpl>
    implements _$$UniversalIndexEntryImplCopyWith<$Res> {
  __$$UniversalIndexEntryImplCopyWithImpl(_$UniversalIndexEntryImpl _value,
      $Res Function(_$UniversalIndexEntryImpl) _then)
      : super(_value, _then);

  /// Create a copy of UniversalIndexEntry
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? connectorId = null,
    Object? contentType = null,
    Object? primaryKey = null,
    Object? searchableText = null,
    Object? displayName = null,
    Object? indexTier = null,
    Object? priority = null,
    Object? indexedAt = null,
    Object? lastModified = freezed,
    Object? lastAccessed = freezed,
    Object? structuredData = null,
    Object? metadata = null,
    Object? keywords = null,
    Object? tags = null,
    Object? score = null,
    Object? snippet = freezed,
    Object? title = null,
    Object? summary = freezed,
    Object? content = freezed,
  }) {
    return _then(_$UniversalIndexEntryImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      connectorId: null == connectorId
          ? _value.connectorId
          : connectorId // ignore: cast_nullable_to_non_nullable
              as String,
      contentType: null == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as UniversalContentType,
      primaryKey: null == primaryKey
          ? _value.primaryKey
          : primaryKey // ignore: cast_nullable_to_non_nullable
              as String,
      searchableText: null == searchableText
          ? _value.searchableText
          : searchableText // ignore: cast_nullable_to_non_nullable
              as String,
      displayName: null == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String,
      indexTier: null == indexTier
          ? _value.indexTier
          : indexTier // ignore: cast_nullable_to_non_nullable
              as IndexTier,
      priority: null == priority
          ? _value.priority
          : priority // ignore: cast_nullable_to_non_nullable
              as int,
      indexedAt: null == indexedAt
          ? _value.indexedAt
          : indexedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      lastModified: freezed == lastModified
          ? _value.lastModified
          : lastModified // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastAccessed: freezed == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      structuredData: null == structuredData
          ? _value._structuredData
          : structuredData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      metadata: null == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      keywords: null == keywords
          ? _value._keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>,
      tags: null == tags
          ? _value._tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      score: null == score
          ? _value.score
          : score // ignore: cast_nullable_to_non_nullable
              as double,
      snippet: freezed == snippet
          ? _value.snippet
          : snippet // ignore: cast_nullable_to_non_nullable
              as String?,
      title: null == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String,
      summary: freezed == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as String?,
      content: freezed == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UniversalIndexEntryImpl
    with DiagnosticableTreeMixin
    implements _UniversalIndexEntry {
  const _$UniversalIndexEntryImpl(
      {required this.id,
      required this.connectorId,
      required this.contentType,
      required this.primaryKey,
      required this.searchableText,
      required this.displayName,
      required this.indexTier,
      this.priority = 5,
      required this.indexedAt,
      this.lastModified,
      this.lastAccessed,
      final Map<String, dynamic> structuredData = const {},
      final Map<String, dynamic> metadata = const {},
      final List<String> keywords = const [],
      final List<String> tags = const [],
      this.score = 0.0,
      this.snippet,
      this.title = '',
      this.summary,
      this.content})
      : _structuredData = structuredData,
        _metadata = metadata,
        _keywords = keywords,
        _tags = tags;

  factory _$UniversalIndexEntryImpl.fromJson(Map<String, dynamic> json) =>
      _$$UniversalIndexEntryImplFromJson(json);

  @override
  final String id;
  @override
  final String connectorId;
  @override
  final UniversalContentType contentType;
  @override
  final String primaryKey;
  @override
  final String searchableText;
  @override
  final String displayName;
  @override
  final IndexTier indexTier;
  @override
  @JsonKey()
  final int priority;
  @override
  final DateTime indexedAt;
  @override
  final DateTime? lastModified;
  @override
  final DateTime? lastAccessed;
  final Map<String, dynamic> _structuredData;
  @override
  @JsonKey()
  Map<String, dynamic> get structuredData {
    if (_structuredData is EqualUnmodifiableMapView) return _structuredData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_structuredData);
  }

  final Map<String, dynamic> _metadata;
  @override
  @JsonKey()
  Map<String, dynamic> get metadata {
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_metadata);
  }

  final List<String> _keywords;
  @override
  @JsonKey()
  List<String> get keywords {
    if (_keywords is EqualUnmodifiableListView) return _keywords;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_keywords);
  }

  final List<String> _tags;
  @override
  @JsonKey()
  List<String> get tags {
    if (_tags is EqualUnmodifiableListView) return _tags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tags);
  }

// 搜索相关字段
  @override
  @JsonKey()
  final double score;
  @override
  final String? snippet;
// 扩展方法需要的字段
  @override
  @JsonKey()
  final String title;
  @override
  final String? summary;
  @override
  final String? content;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'UniversalIndexEntry(id: $id, connectorId: $connectorId, contentType: $contentType, primaryKey: $primaryKey, searchableText: $searchableText, displayName: $displayName, indexTier: $indexTier, priority: $priority, indexedAt: $indexedAt, lastModified: $lastModified, lastAccessed: $lastAccessed, structuredData: $structuredData, metadata: $metadata, keywords: $keywords, tags: $tags, score: $score, snippet: $snippet, title: $title, summary: $summary, content: $content)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'UniversalIndexEntry'))
      ..add(DiagnosticsProperty('id', id))
      ..add(DiagnosticsProperty('connectorId', connectorId))
      ..add(DiagnosticsProperty('contentType', contentType))
      ..add(DiagnosticsProperty('primaryKey', primaryKey))
      ..add(DiagnosticsProperty('searchableText', searchableText))
      ..add(DiagnosticsProperty('displayName', displayName))
      ..add(DiagnosticsProperty('indexTier', indexTier))
      ..add(DiagnosticsProperty('priority', priority))
      ..add(DiagnosticsProperty('indexedAt', indexedAt))
      ..add(DiagnosticsProperty('lastModified', lastModified))
      ..add(DiagnosticsProperty('lastAccessed', lastAccessed))
      ..add(DiagnosticsProperty('structuredData', structuredData))
      ..add(DiagnosticsProperty('metadata', metadata))
      ..add(DiagnosticsProperty('keywords', keywords))
      ..add(DiagnosticsProperty('tags', tags))
      ..add(DiagnosticsProperty('score', score))
      ..add(DiagnosticsProperty('snippet', snippet))
      ..add(DiagnosticsProperty('title', title))
      ..add(DiagnosticsProperty('summary', summary))
      ..add(DiagnosticsProperty('content', content));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UniversalIndexEntryImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.connectorId, connectorId) ||
                other.connectorId == connectorId) &&
            (identical(other.contentType, contentType) ||
                other.contentType == contentType) &&
            (identical(other.primaryKey, primaryKey) ||
                other.primaryKey == primaryKey) &&
            (identical(other.searchableText, searchableText) ||
                other.searchableText == searchableText) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.indexTier, indexTier) ||
                other.indexTier == indexTier) &&
            (identical(other.priority, priority) ||
                other.priority == priority) &&
            (identical(other.indexedAt, indexedAt) ||
                other.indexedAt == indexedAt) &&
            (identical(other.lastModified, lastModified) ||
                other.lastModified == lastModified) &&
            (identical(other.lastAccessed, lastAccessed) ||
                other.lastAccessed == lastAccessed) &&
            const DeepCollectionEquality()
                .equals(other._structuredData, _structuredData) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            const DeepCollectionEquality().equals(other._keywords, _keywords) &&
            const DeepCollectionEquality().equals(other._tags, _tags) &&
            (identical(other.score, score) || other.score == score) &&
            (identical(other.snippet, snippet) || other.snippet == snippet) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.summary, summary) || other.summary == summary) &&
            (identical(other.content, content) || other.content == content));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        connectorId,
        contentType,
        primaryKey,
        searchableText,
        displayName,
        indexTier,
        priority,
        indexedAt,
        lastModified,
        lastAccessed,
        const DeepCollectionEquality().hash(_structuredData),
        const DeepCollectionEquality().hash(_metadata),
        const DeepCollectionEquality().hash(_keywords),
        const DeepCollectionEquality().hash(_tags),
        score,
        snippet,
        title,
        summary,
        content
      ]);

  /// Create a copy of UniversalIndexEntry
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UniversalIndexEntryImplCopyWith<_$UniversalIndexEntryImpl> get copyWith =>
      __$$UniversalIndexEntryImplCopyWithImpl<_$UniversalIndexEntryImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UniversalIndexEntryImplToJson(
      this,
    );
  }
}

abstract class _UniversalIndexEntry implements UniversalIndexEntry {
  const factory _UniversalIndexEntry(
      {required final String id,
      required final String connectorId,
      required final UniversalContentType contentType,
      required final String primaryKey,
      required final String searchableText,
      required final String displayName,
      required final IndexTier indexTier,
      final int priority,
      required final DateTime indexedAt,
      final DateTime? lastModified,
      final DateTime? lastAccessed,
      final Map<String, dynamic> structuredData,
      final Map<String, dynamic> metadata,
      final List<String> keywords,
      final List<String> tags,
      final double score,
      final String? snippet,
      final String title,
      final String? summary,
      final String? content}) = _$UniversalIndexEntryImpl;

  factory _UniversalIndexEntry.fromJson(Map<String, dynamic> json) =
      _$UniversalIndexEntryImpl.fromJson;

  @override
  String get id;
  @override
  String get connectorId;
  @override
  UniversalContentType get contentType;
  @override
  String get primaryKey;
  @override
  String get searchableText;
  @override
  String get displayName;
  @override
  IndexTier get indexTier;
  @override
  int get priority;
  @override
  DateTime get indexedAt;
  @override
  DateTime? get lastModified;
  @override
  DateTime? get lastAccessed;
  @override
  Map<String, dynamic> get structuredData;
  @override
  Map<String, dynamic> get metadata;
  @override
  List<String> get keywords;
  @override
  List<String> get tags; // 搜索相关字段
  @override
  double get score;
  @override
  String? get snippet; // 扩展方法需要的字段
  @override
  String get title;
  @override
  String? get summary;
  @override
  String? get content;

  /// Create a copy of UniversalIndexEntry
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UniversalIndexEntryImplCopyWith<_$UniversalIndexEntryImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IndexSearchResult _$IndexSearchResultFromJson(Map<String, dynamic> json) {
  return _IndexSearchResult.fromJson(json);
}

/// @nodoc
mixin _$IndexSearchResult {
  String get query => throw _privateConstructorUsedError;
  List<UniversalIndexEntry> get results => throw _privateConstructorUsedError;
  int get totalCount => throw _privateConstructorUsedError;
  Duration get searchTime => throw _privateConstructorUsedError;
  Map<String, int>? get facets => throw _privateConstructorUsedError;

  /// Serializes this IndexSearchResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of IndexSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $IndexSearchResultCopyWith<IndexSearchResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IndexSearchResultCopyWith<$Res> {
  factory $IndexSearchResultCopyWith(
          IndexSearchResult value, $Res Function(IndexSearchResult) then) =
      _$IndexSearchResultCopyWithImpl<$Res, IndexSearchResult>;
  @useResult
  $Res call(
      {String query,
      List<UniversalIndexEntry> results,
      int totalCount,
      Duration searchTime,
      Map<String, int>? facets});
}

/// @nodoc
class _$IndexSearchResultCopyWithImpl<$Res, $Val extends IndexSearchResult>
    implements $IndexSearchResultCopyWith<$Res> {
  _$IndexSearchResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of IndexSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? query = null,
    Object? results = null,
    Object? totalCount = null,
    Object? searchTime = null,
    Object? facets = freezed,
  }) {
    return _then(_value.copyWith(
      query: null == query
          ? _value.query
          : query // ignore: cast_nullable_to_non_nullable
              as String,
      results: null == results
          ? _value.results
          : results // ignore: cast_nullable_to_non_nullable
              as List<UniversalIndexEntry>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      searchTime: null == searchTime
          ? _value.searchTime
          : searchTime // ignore: cast_nullable_to_non_nullable
              as Duration,
      facets: freezed == facets
          ? _value.facets
          : facets // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IndexSearchResultImplCopyWith<$Res>
    implements $IndexSearchResultCopyWith<$Res> {
  factory _$$IndexSearchResultImplCopyWith(_$IndexSearchResultImpl value,
          $Res Function(_$IndexSearchResultImpl) then) =
      __$$IndexSearchResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String query,
      List<UniversalIndexEntry> results,
      int totalCount,
      Duration searchTime,
      Map<String, int>? facets});
}

/// @nodoc
class __$$IndexSearchResultImplCopyWithImpl<$Res>
    extends _$IndexSearchResultCopyWithImpl<$Res, _$IndexSearchResultImpl>
    implements _$$IndexSearchResultImplCopyWith<$Res> {
  __$$IndexSearchResultImplCopyWithImpl(_$IndexSearchResultImpl _value,
      $Res Function(_$IndexSearchResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of IndexSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? query = null,
    Object? results = null,
    Object? totalCount = null,
    Object? searchTime = null,
    Object? facets = freezed,
  }) {
    return _then(_$IndexSearchResultImpl(
      query: null == query
          ? _value.query
          : query // ignore: cast_nullable_to_non_nullable
              as String,
      results: null == results
          ? _value._results
          : results // ignore: cast_nullable_to_non_nullable
              as List<UniversalIndexEntry>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      searchTime: null == searchTime
          ? _value.searchTime
          : searchTime // ignore: cast_nullable_to_non_nullable
              as Duration,
      facets: freezed == facets
          ? _value._facets
          : facets // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IndexSearchResultImpl
    with DiagnosticableTreeMixin
    implements _IndexSearchResult {
  const _$IndexSearchResultImpl(
      {required this.query,
      required final List<UniversalIndexEntry> results,
      required this.totalCount,
      required this.searchTime,
      final Map<String, int>? facets})
      : _results = results,
        _facets = facets;

  factory _$IndexSearchResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$IndexSearchResultImplFromJson(json);

  @override
  final String query;
  final List<UniversalIndexEntry> _results;
  @override
  List<UniversalIndexEntry> get results {
    if (_results is EqualUnmodifiableListView) return _results;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_results);
  }

  @override
  final int totalCount;
  @override
  final Duration searchTime;
  final Map<String, int>? _facets;
  @override
  Map<String, int>? get facets {
    final value = _facets;
    if (value == null) return null;
    if (_facets is EqualUnmodifiableMapView) return _facets;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'IndexSearchResult(query: $query, results: $results, totalCount: $totalCount, searchTime: $searchTime, facets: $facets)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'IndexSearchResult'))
      ..add(DiagnosticsProperty('query', query))
      ..add(DiagnosticsProperty('results', results))
      ..add(DiagnosticsProperty('totalCount', totalCount))
      ..add(DiagnosticsProperty('searchTime', searchTime))
      ..add(DiagnosticsProperty('facets', facets));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IndexSearchResultImpl &&
            (identical(other.query, query) || other.query == query) &&
            const DeepCollectionEquality().equals(other._results, _results) &&
            (identical(other.totalCount, totalCount) ||
                other.totalCount == totalCount) &&
            (identical(other.searchTime, searchTime) ||
                other.searchTime == searchTime) &&
            const DeepCollectionEquality().equals(other._facets, _facets));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      query,
      const DeepCollectionEquality().hash(_results),
      totalCount,
      searchTime,
      const DeepCollectionEquality().hash(_facets));

  /// Create a copy of IndexSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$IndexSearchResultImplCopyWith<_$IndexSearchResultImpl> get copyWith =>
      __$$IndexSearchResultImplCopyWithImpl<_$IndexSearchResultImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IndexSearchResultImplToJson(
      this,
    );
  }
}

abstract class _IndexSearchResult implements IndexSearchResult {
  const factory _IndexSearchResult(
      {required final String query,
      required final List<UniversalIndexEntry> results,
      required final int totalCount,
      required final Duration searchTime,
      final Map<String, int>? facets}) = _$IndexSearchResultImpl;

  factory _IndexSearchResult.fromJson(Map<String, dynamic> json) =
      _$IndexSearchResultImpl.fromJson;

  @override
  String get query;
  @override
  List<UniversalIndexEntry> get results;
  @override
  int get totalCount;
  @override
  Duration get searchTime;
  @override
  Map<String, int>? get facets;

  /// Create a copy of IndexSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$IndexSearchResultImplCopyWith<_$IndexSearchResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

UnifiedEntityMetadata _$UnifiedEntityMetadataFromJson(
    Map<String, dynamic> json) {
  return _UnifiedEntityMetadata.fromJson(json);
}

/// @nodoc
mixin _$UnifiedEntityMetadata {
  String get entityId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  UnifiedEntityType get type => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  Map<String, dynamic>? get properties => throw _privateConstructorUsedError;
  List<String> get tags => throw _privateConstructorUsedError;
  int get accessCount => throw _privateConstructorUsedError;
  DateTime? get lastAccessed => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError; // 扩展字段用于星空可视化
  String? get entityType => throw _privateConstructorUsedError;
  String? get displayName => throw _privateConstructorUsedError;
  double get importance => throw _privateConstructorUsedError;

  /// Serializes this UnifiedEntityMetadata to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UnifiedEntityMetadata
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UnifiedEntityMetadataCopyWith<UnifiedEntityMetadata> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UnifiedEntityMetadataCopyWith<$Res> {
  factory $UnifiedEntityMetadataCopyWith(UnifiedEntityMetadata value,
          $Res Function(UnifiedEntityMetadata) then) =
      _$UnifiedEntityMetadataCopyWithImpl<$Res, UnifiedEntityMetadata>;
  @useResult
  $Res call(
      {String entityId,
      String name,
      UnifiedEntityType type,
      String? description,
      Map<String, dynamic>? properties,
      List<String> tags,
      int accessCount,
      DateTime? lastAccessed,
      DateTime createdAt,
      DateTime updatedAt,
      String? entityType,
      String? displayName,
      double importance});
}

/// @nodoc
class _$UnifiedEntityMetadataCopyWithImpl<$Res,
        $Val extends UnifiedEntityMetadata>
    implements $UnifiedEntityMetadataCopyWith<$Res> {
  _$UnifiedEntityMetadataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UnifiedEntityMetadata
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entityId = null,
    Object? name = null,
    Object? type = null,
    Object? description = freezed,
    Object? properties = freezed,
    Object? tags = null,
    Object? accessCount = null,
    Object? lastAccessed = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? entityType = freezed,
    Object? displayName = freezed,
    Object? importance = null,
  }) {
    return _then(_value.copyWith(
      entityId: null == entityId
          ? _value.entityId
          : entityId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as UnifiedEntityType,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      properties: freezed == properties
          ? _value.properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      tags: null == tags
          ? _value.tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      accessCount: null == accessCount
          ? _value.accessCount
          : accessCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastAccessed: freezed == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      entityType: freezed == entityType
          ? _value.entityType
          : entityType // ignore: cast_nullable_to_non_nullable
              as String?,
      displayName: freezed == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      importance: null == importance
          ? _value.importance
          : importance // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UnifiedEntityMetadataImplCopyWith<$Res>
    implements $UnifiedEntityMetadataCopyWith<$Res> {
  factory _$$UnifiedEntityMetadataImplCopyWith(
          _$UnifiedEntityMetadataImpl value,
          $Res Function(_$UnifiedEntityMetadataImpl) then) =
      __$$UnifiedEntityMetadataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String entityId,
      String name,
      UnifiedEntityType type,
      String? description,
      Map<String, dynamic>? properties,
      List<String> tags,
      int accessCount,
      DateTime? lastAccessed,
      DateTime createdAt,
      DateTime updatedAt,
      String? entityType,
      String? displayName,
      double importance});
}

/// @nodoc
class __$$UnifiedEntityMetadataImplCopyWithImpl<$Res>
    extends _$UnifiedEntityMetadataCopyWithImpl<$Res,
        _$UnifiedEntityMetadataImpl>
    implements _$$UnifiedEntityMetadataImplCopyWith<$Res> {
  __$$UnifiedEntityMetadataImplCopyWithImpl(_$UnifiedEntityMetadataImpl _value,
      $Res Function(_$UnifiedEntityMetadataImpl) _then)
      : super(_value, _then);

  /// Create a copy of UnifiedEntityMetadata
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entityId = null,
    Object? name = null,
    Object? type = null,
    Object? description = freezed,
    Object? properties = freezed,
    Object? tags = null,
    Object? accessCount = null,
    Object? lastAccessed = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? entityType = freezed,
    Object? displayName = freezed,
    Object? importance = null,
  }) {
    return _then(_$UnifiedEntityMetadataImpl(
      entityId: null == entityId
          ? _value.entityId
          : entityId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as UnifiedEntityType,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      properties: freezed == properties
          ? _value._properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      tags: null == tags
          ? _value._tags
          : tags // ignore: cast_nullable_to_non_nullable
              as List<String>,
      accessCount: null == accessCount
          ? _value.accessCount
          : accessCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastAccessed: freezed == lastAccessed
          ? _value.lastAccessed
          : lastAccessed // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      entityType: freezed == entityType
          ? _value.entityType
          : entityType // ignore: cast_nullable_to_non_nullable
              as String?,
      displayName: freezed == displayName
          ? _value.displayName
          : displayName // ignore: cast_nullable_to_non_nullable
              as String?,
      importance: null == importance
          ? _value.importance
          : importance // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UnifiedEntityMetadataImpl
    with DiagnosticableTreeMixin
    implements _UnifiedEntityMetadata {
  const _$UnifiedEntityMetadataImpl(
      {required this.entityId,
      required this.name,
      required this.type,
      this.description,
      final Map<String, dynamic>? properties,
      final List<String> tags = const [],
      this.accessCount = 0,
      this.lastAccessed,
      required this.createdAt,
      required this.updatedAt,
      this.entityType,
      this.displayName,
      this.importance = 0.0})
      : _properties = properties,
        _tags = tags;

  factory _$UnifiedEntityMetadataImpl.fromJson(Map<String, dynamic> json) =>
      _$$UnifiedEntityMetadataImplFromJson(json);

  @override
  final String entityId;
  @override
  final String name;
  @override
  final UnifiedEntityType type;
  @override
  final String? description;
  final Map<String, dynamic>? _properties;
  @override
  Map<String, dynamic>? get properties {
    final value = _properties;
    if (value == null) return null;
    if (_properties is EqualUnmodifiableMapView) return _properties;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final List<String> _tags;
  @override
  @JsonKey()
  List<String> get tags {
    if (_tags is EqualUnmodifiableListView) return _tags;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_tags);
  }

  @override
  @JsonKey()
  final int accessCount;
  @override
  final DateTime? lastAccessed;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;
// 扩展字段用于星空可视化
  @override
  final String? entityType;
  @override
  final String? displayName;
  @override
  @JsonKey()
  final double importance;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'UnifiedEntityMetadata(entityId: $entityId, name: $name, type: $type, description: $description, properties: $properties, tags: $tags, accessCount: $accessCount, lastAccessed: $lastAccessed, createdAt: $createdAt, updatedAt: $updatedAt, entityType: $entityType, displayName: $displayName, importance: $importance)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'UnifiedEntityMetadata'))
      ..add(DiagnosticsProperty('entityId', entityId))
      ..add(DiagnosticsProperty('name', name))
      ..add(DiagnosticsProperty('type', type))
      ..add(DiagnosticsProperty('description', description))
      ..add(DiagnosticsProperty('properties', properties))
      ..add(DiagnosticsProperty('tags', tags))
      ..add(DiagnosticsProperty('accessCount', accessCount))
      ..add(DiagnosticsProperty('lastAccessed', lastAccessed))
      ..add(DiagnosticsProperty('createdAt', createdAt))
      ..add(DiagnosticsProperty('updatedAt', updatedAt))
      ..add(DiagnosticsProperty('entityType', entityType))
      ..add(DiagnosticsProperty('displayName', displayName))
      ..add(DiagnosticsProperty('importance', importance));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UnifiedEntityMetadataImpl &&
            (identical(other.entityId, entityId) ||
                other.entityId == entityId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality()
                .equals(other._properties, _properties) &&
            const DeepCollectionEquality().equals(other._tags, _tags) &&
            (identical(other.accessCount, accessCount) ||
                other.accessCount == accessCount) &&
            (identical(other.lastAccessed, lastAccessed) ||
                other.lastAccessed == lastAccessed) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            (identical(other.entityType, entityType) ||
                other.entityType == entityType) &&
            (identical(other.displayName, displayName) ||
                other.displayName == displayName) &&
            (identical(other.importance, importance) ||
                other.importance == importance));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      entityId,
      name,
      type,
      description,
      const DeepCollectionEquality().hash(_properties),
      const DeepCollectionEquality().hash(_tags),
      accessCount,
      lastAccessed,
      createdAt,
      updatedAt,
      entityType,
      displayName,
      importance);

  /// Create a copy of UnifiedEntityMetadata
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UnifiedEntityMetadataImplCopyWith<_$UnifiedEntityMetadataImpl>
      get copyWith => __$$UnifiedEntityMetadataImplCopyWithImpl<
          _$UnifiedEntityMetadataImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UnifiedEntityMetadataImplToJson(
      this,
    );
  }
}

abstract class _UnifiedEntityMetadata implements UnifiedEntityMetadata {
  const factory _UnifiedEntityMetadata(
      {required final String entityId,
      required final String name,
      required final UnifiedEntityType type,
      final String? description,
      final Map<String, dynamic>? properties,
      final List<String> tags,
      final int accessCount,
      final DateTime? lastAccessed,
      required final DateTime createdAt,
      required final DateTime updatedAt,
      final String? entityType,
      final String? displayName,
      final double importance}) = _$UnifiedEntityMetadataImpl;

  factory _UnifiedEntityMetadata.fromJson(Map<String, dynamic> json) =
      _$UnifiedEntityMetadataImpl.fromJson;

  @override
  String get entityId;
  @override
  String get name;
  @override
  UnifiedEntityType get type;
  @override
  String? get description;
  @override
  Map<String, dynamic>? get properties;
  @override
  List<String> get tags;
  @override
  int get accessCount;
  @override
  DateTime? get lastAccessed;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt; // 扩展字段用于星空可视化
  @override
  String? get entityType;
  @override
  String? get displayName;
  @override
  double get importance;

  /// Create a copy of UnifiedEntityMetadata
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UnifiedEntityMetadataImplCopyWith<_$UnifiedEntityMetadataImpl>
      get copyWith => throw _privateConstructorUsedError;
}

UnifiedEntityRelationship _$UnifiedEntityRelationshipFromJson(
    Map<String, dynamic> json) {
  return _UnifiedEntityRelationship.fromJson(json);
}

/// @nodoc
mixin _$UnifiedEntityRelationship {
  String get sourceEntityId => throw _privateConstructorUsedError;
  String get targetEntityId => throw _privateConstructorUsedError;
  String get relationshipType => throw _privateConstructorUsedError;
  int get strength => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  Map<String, dynamic>? get properties => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this UnifiedEntityRelationship to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UnifiedEntityRelationship
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UnifiedEntityRelationshipCopyWith<UnifiedEntityRelationship> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UnifiedEntityRelationshipCopyWith<$Res> {
  factory $UnifiedEntityRelationshipCopyWith(UnifiedEntityRelationship value,
          $Res Function(UnifiedEntityRelationship) then) =
      _$UnifiedEntityRelationshipCopyWithImpl<$Res, UnifiedEntityRelationship>;
  @useResult
  $Res call(
      {String sourceEntityId,
      String targetEntityId,
      String relationshipType,
      int strength,
      String? description,
      Map<String, dynamic>? properties,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class _$UnifiedEntityRelationshipCopyWithImpl<$Res,
        $Val extends UnifiedEntityRelationship>
    implements $UnifiedEntityRelationshipCopyWith<$Res> {
  _$UnifiedEntityRelationshipCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UnifiedEntityRelationship
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? sourceEntityId = null,
    Object? targetEntityId = null,
    Object? relationshipType = null,
    Object? strength = null,
    Object? description = freezed,
    Object? properties = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      sourceEntityId: null == sourceEntityId
          ? _value.sourceEntityId
          : sourceEntityId // ignore: cast_nullable_to_non_nullable
              as String,
      targetEntityId: null == targetEntityId
          ? _value.targetEntityId
          : targetEntityId // ignore: cast_nullable_to_non_nullable
              as String,
      relationshipType: null == relationshipType
          ? _value.relationshipType
          : relationshipType // ignore: cast_nullable_to_non_nullable
              as String,
      strength: null == strength
          ? _value.strength
          : strength // ignore: cast_nullable_to_non_nullable
              as int,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      properties: freezed == properties
          ? _value.properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UnifiedEntityRelationshipImplCopyWith<$Res>
    implements $UnifiedEntityRelationshipCopyWith<$Res> {
  factory _$$UnifiedEntityRelationshipImplCopyWith(
          _$UnifiedEntityRelationshipImpl value,
          $Res Function(_$UnifiedEntityRelationshipImpl) then) =
      __$$UnifiedEntityRelationshipImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String sourceEntityId,
      String targetEntityId,
      String relationshipType,
      int strength,
      String? description,
      Map<String, dynamic>? properties,
      DateTime createdAt,
      DateTime updatedAt});
}

/// @nodoc
class __$$UnifiedEntityRelationshipImplCopyWithImpl<$Res>
    extends _$UnifiedEntityRelationshipCopyWithImpl<$Res,
        _$UnifiedEntityRelationshipImpl>
    implements _$$UnifiedEntityRelationshipImplCopyWith<$Res> {
  __$$UnifiedEntityRelationshipImplCopyWithImpl(
      _$UnifiedEntityRelationshipImpl _value,
      $Res Function(_$UnifiedEntityRelationshipImpl) _then)
      : super(_value, _then);

  /// Create a copy of UnifiedEntityRelationship
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? sourceEntityId = null,
    Object? targetEntityId = null,
    Object? relationshipType = null,
    Object? strength = null,
    Object? description = freezed,
    Object? properties = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$UnifiedEntityRelationshipImpl(
      sourceEntityId: null == sourceEntityId
          ? _value.sourceEntityId
          : sourceEntityId // ignore: cast_nullable_to_non_nullable
              as String,
      targetEntityId: null == targetEntityId
          ? _value.targetEntityId
          : targetEntityId // ignore: cast_nullable_to_non_nullable
              as String,
      relationshipType: null == relationshipType
          ? _value.relationshipType
          : relationshipType // ignore: cast_nullable_to_non_nullable
              as String,
      strength: null == strength
          ? _value.strength
          : strength // ignore: cast_nullable_to_non_nullable
              as int,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      properties: freezed == properties
          ? _value._properties
          : properties // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UnifiedEntityRelationshipImpl
    with DiagnosticableTreeMixin
    implements _UnifiedEntityRelationship {
  const _$UnifiedEntityRelationshipImpl(
      {required this.sourceEntityId,
      required this.targetEntityId,
      required this.relationshipType,
      this.strength = 1,
      this.description,
      final Map<String, dynamic>? properties,
      required this.createdAt,
      required this.updatedAt})
      : _properties = properties;

  factory _$UnifiedEntityRelationshipImpl.fromJson(Map<String, dynamic> json) =>
      _$$UnifiedEntityRelationshipImplFromJson(json);

  @override
  final String sourceEntityId;
  @override
  final String targetEntityId;
  @override
  final String relationshipType;
  @override
  @JsonKey()
  final int strength;
  @override
  final String? description;
  final Map<String, dynamic>? _properties;
  @override
  Map<String, dynamic>? get properties {
    final value = _properties;
    if (value == null) return null;
    if (_properties is EqualUnmodifiableMapView) return _properties;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'UnifiedEntityRelationship(sourceEntityId: $sourceEntityId, targetEntityId: $targetEntityId, relationshipType: $relationshipType, strength: $strength, description: $description, properties: $properties, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'UnifiedEntityRelationship'))
      ..add(DiagnosticsProperty('sourceEntityId', sourceEntityId))
      ..add(DiagnosticsProperty('targetEntityId', targetEntityId))
      ..add(DiagnosticsProperty('relationshipType', relationshipType))
      ..add(DiagnosticsProperty('strength', strength))
      ..add(DiagnosticsProperty('description', description))
      ..add(DiagnosticsProperty('properties', properties))
      ..add(DiagnosticsProperty('createdAt', createdAt))
      ..add(DiagnosticsProperty('updatedAt', updatedAt));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UnifiedEntityRelationshipImpl &&
            (identical(other.sourceEntityId, sourceEntityId) ||
                other.sourceEntityId == sourceEntityId) &&
            (identical(other.targetEntityId, targetEntityId) ||
                other.targetEntityId == targetEntityId) &&
            (identical(other.relationshipType, relationshipType) ||
                other.relationshipType == relationshipType) &&
            (identical(other.strength, strength) ||
                other.strength == strength) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality()
                .equals(other._properties, _properties) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      sourceEntityId,
      targetEntityId,
      relationshipType,
      strength,
      description,
      const DeepCollectionEquality().hash(_properties),
      createdAt,
      updatedAt);

  /// Create a copy of UnifiedEntityRelationship
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UnifiedEntityRelationshipImplCopyWith<_$UnifiedEntityRelationshipImpl>
      get copyWith => __$$UnifiedEntityRelationshipImplCopyWithImpl<
          _$UnifiedEntityRelationshipImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UnifiedEntityRelationshipImplToJson(
      this,
    );
  }
}

abstract class _UnifiedEntityRelationship implements UnifiedEntityRelationship {
  const factory _UnifiedEntityRelationship(
      {required final String sourceEntityId,
      required final String targetEntityId,
      required final String relationshipType,
      final int strength,
      final String? description,
      final Map<String, dynamic>? properties,
      required final DateTime createdAt,
      required final DateTime updatedAt}) = _$UnifiedEntityRelationshipImpl;

  factory _UnifiedEntityRelationship.fromJson(Map<String, dynamic> json) =
      _$UnifiedEntityRelationshipImpl.fromJson;

  @override
  String get sourceEntityId;
  @override
  String get targetEntityId;
  @override
  String get relationshipType;
  @override
  int get strength;
  @override
  String? get description;
  @override
  Map<String, dynamic>? get properties;
  @override
  DateTime get createdAt;
  @override
  DateTime get updatedAt;

  /// Create a copy of UnifiedEntityRelationship
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UnifiedEntityRelationshipImplCopyWith<_$UnifiedEntityRelationshipImpl>
      get copyWith => throw _privateConstructorUsedError;
}

GraphNode _$GraphNodeFromJson(Map<String, dynamic> json) {
  return _GraphNode.fromJson(json);
}

/// @nodoc
mixin _$GraphNode {
  String get id => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  String? get nodeType => throw _privateConstructorUsedError;
  Map<String, dynamic>? get attributes => throw _privateConstructorUsedError;
  double get weight => throw _privateConstructorUsedError;
  double get importance => throw _privateConstructorUsedError;
  double get centralityScore => throw _privateConstructorUsedError;

  /// Serializes this GraphNode to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GraphNodeCopyWith<GraphNode> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GraphNodeCopyWith<$Res> {
  factory $GraphNodeCopyWith(GraphNode value, $Res Function(GraphNode) then) =
      _$GraphNodeCopyWithImpl<$Res, GraphNode>;
  @useResult
  $Res call(
      {String id,
      String label,
      String? nodeType,
      Map<String, dynamic>? attributes,
      double weight,
      double importance,
      double centralityScore});
}

/// @nodoc
class _$GraphNodeCopyWithImpl<$Res, $Val extends GraphNode>
    implements $GraphNodeCopyWith<$Res> {
  _$GraphNodeCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? nodeType = freezed,
    Object? attributes = freezed,
    Object? weight = null,
    Object? importance = null,
    Object? centralityScore = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      nodeType: freezed == nodeType
          ? _value.nodeType
          : nodeType // ignore: cast_nullable_to_non_nullable
              as String?,
      attributes: freezed == attributes
          ? _value.attributes
          : attributes // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as double,
      importance: null == importance
          ? _value.importance
          : importance // ignore: cast_nullable_to_non_nullable
              as double,
      centralityScore: null == centralityScore
          ? _value.centralityScore
          : centralityScore // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$GraphNodeImplCopyWith<$Res>
    implements $GraphNodeCopyWith<$Res> {
  factory _$$GraphNodeImplCopyWith(
          _$GraphNodeImpl value, $Res Function(_$GraphNodeImpl) then) =
      __$$GraphNodeImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String label,
      String? nodeType,
      Map<String, dynamic>? attributes,
      double weight,
      double importance,
      double centralityScore});
}

/// @nodoc
class __$$GraphNodeImplCopyWithImpl<$Res>
    extends _$GraphNodeCopyWithImpl<$Res, _$GraphNodeImpl>
    implements _$$GraphNodeImplCopyWith<$Res> {
  __$$GraphNodeImplCopyWithImpl(
      _$GraphNodeImpl _value, $Res Function(_$GraphNodeImpl) _then)
      : super(_value, _then);

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = null,
    Object? nodeType = freezed,
    Object? attributes = freezed,
    Object? weight = null,
    Object? importance = null,
    Object? centralityScore = null,
  }) {
    return _then(_$GraphNodeImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      nodeType: freezed == nodeType
          ? _value.nodeType
          : nodeType // ignore: cast_nullable_to_non_nullable
              as String?,
      attributes: freezed == attributes
          ? _value._attributes
          : attributes // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as double,
      importance: null == importance
          ? _value.importance
          : importance // ignore: cast_nullable_to_non_nullable
              as double,
      centralityScore: null == centralityScore
          ? _value.centralityScore
          : centralityScore // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$GraphNodeImpl with DiagnosticableTreeMixin implements _GraphNode {
  const _$GraphNodeImpl(
      {required this.id,
      required this.label,
      this.nodeType,
      final Map<String, dynamic>? attributes,
      this.weight = 1.0,
      this.importance = 1.0,
      this.centralityScore = 0.0})
      : _attributes = attributes;

  factory _$GraphNodeImpl.fromJson(Map<String, dynamic> json) =>
      _$$GraphNodeImplFromJson(json);

  @override
  final String id;
  @override
  final String label;
  @override
  final String? nodeType;
  final Map<String, dynamic>? _attributes;
  @override
  Map<String, dynamic>? get attributes {
    final value = _attributes;
    if (value == null) return null;
    if (_attributes is EqualUnmodifiableMapView) return _attributes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  @JsonKey()
  final double weight;
  @override
  @JsonKey()
  final double importance;
  @override
  @JsonKey()
  final double centralityScore;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'GraphNode(id: $id, label: $label, nodeType: $nodeType, attributes: $attributes, weight: $weight, importance: $importance, centralityScore: $centralityScore)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'GraphNode'))
      ..add(DiagnosticsProperty('id', id))
      ..add(DiagnosticsProperty('label', label))
      ..add(DiagnosticsProperty('nodeType', nodeType))
      ..add(DiagnosticsProperty('attributes', attributes))
      ..add(DiagnosticsProperty('weight', weight))
      ..add(DiagnosticsProperty('importance', importance))
      ..add(DiagnosticsProperty('centralityScore', centralityScore));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GraphNodeImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.nodeType, nodeType) ||
                other.nodeType == nodeType) &&
            const DeepCollectionEquality()
                .equals(other._attributes, _attributes) &&
            (identical(other.weight, weight) || other.weight == weight) &&
            (identical(other.importance, importance) ||
                other.importance == importance) &&
            (identical(other.centralityScore, centralityScore) ||
                other.centralityScore == centralityScore));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      label,
      nodeType,
      const DeepCollectionEquality().hash(_attributes),
      weight,
      importance,
      centralityScore);

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GraphNodeImplCopyWith<_$GraphNodeImpl> get copyWith =>
      __$$GraphNodeImplCopyWithImpl<_$GraphNodeImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GraphNodeImplToJson(
      this,
    );
  }
}

abstract class _GraphNode implements GraphNode {
  const factory _GraphNode(
      {required final String id,
      required final String label,
      final String? nodeType,
      final Map<String, dynamic>? attributes,
      final double weight,
      final double importance,
      final double centralityScore}) = _$GraphNodeImpl;

  factory _GraphNode.fromJson(Map<String, dynamic> json) =
      _$GraphNodeImpl.fromJson;

  @override
  String get id;
  @override
  String get label;
  @override
  String? get nodeType;
  @override
  Map<String, dynamic>? get attributes;
  @override
  double get weight;
  @override
  double get importance;
  @override
  double get centralityScore;

  /// Create a copy of GraphNode
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GraphNodeImplCopyWith<_$GraphNodeImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

GraphEdge _$GraphEdgeFromJson(Map<String, dynamic> json) {
  return _GraphEdge.fromJson(json);
}

/// @nodoc
mixin _$GraphEdge {
  String get source => throw _privateConstructorUsedError;
  String get target => throw _privateConstructorUsedError;
  String? get edgeType => throw _privateConstructorUsedError;
  double get weight => throw _privateConstructorUsedError;
  Map<String, dynamic>? get attributes => throw _privateConstructorUsedError;

  /// Serializes this GraphEdge to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $GraphEdgeCopyWith<GraphEdge> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $GraphEdgeCopyWith<$Res> {
  factory $GraphEdgeCopyWith(GraphEdge value, $Res Function(GraphEdge) then) =
      _$GraphEdgeCopyWithImpl<$Res, GraphEdge>;
  @useResult
  $Res call(
      {String source,
      String target,
      String? edgeType,
      double weight,
      Map<String, dynamic>? attributes});
}

/// @nodoc
class _$GraphEdgeCopyWithImpl<$Res, $Val extends GraphEdge>
    implements $GraphEdgeCopyWith<$Res> {
  _$GraphEdgeCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? source = null,
    Object? target = null,
    Object? edgeType = freezed,
    Object? weight = null,
    Object? attributes = freezed,
  }) {
    return _then(_value.copyWith(
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      target: null == target
          ? _value.target
          : target // ignore: cast_nullable_to_non_nullable
              as String,
      edgeType: freezed == edgeType
          ? _value.edgeType
          : edgeType // ignore: cast_nullable_to_non_nullable
              as String?,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as double,
      attributes: freezed == attributes
          ? _value.attributes
          : attributes // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$GraphEdgeImplCopyWith<$Res>
    implements $GraphEdgeCopyWith<$Res> {
  factory _$$GraphEdgeImplCopyWith(
          _$GraphEdgeImpl value, $Res Function(_$GraphEdgeImpl) then) =
      __$$GraphEdgeImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String source,
      String target,
      String? edgeType,
      double weight,
      Map<String, dynamic>? attributes});
}

/// @nodoc
class __$$GraphEdgeImplCopyWithImpl<$Res>
    extends _$GraphEdgeCopyWithImpl<$Res, _$GraphEdgeImpl>
    implements _$$GraphEdgeImplCopyWith<$Res> {
  __$$GraphEdgeImplCopyWithImpl(
      _$GraphEdgeImpl _value, $Res Function(_$GraphEdgeImpl) _then)
      : super(_value, _then);

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? source = null,
    Object? target = null,
    Object? edgeType = freezed,
    Object? weight = null,
    Object? attributes = freezed,
  }) {
    return _then(_$GraphEdgeImpl(
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as String,
      target: null == target
          ? _value.target
          : target // ignore: cast_nullable_to_non_nullable
              as String,
      edgeType: freezed == edgeType
          ? _value.edgeType
          : edgeType // ignore: cast_nullable_to_non_nullable
              as String?,
      weight: null == weight
          ? _value.weight
          : weight // ignore: cast_nullable_to_non_nullable
              as double,
      attributes: freezed == attributes
          ? _value._attributes
          : attributes // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$GraphEdgeImpl with DiagnosticableTreeMixin implements _GraphEdge {
  const _$GraphEdgeImpl(
      {required this.source,
      required this.target,
      this.edgeType,
      this.weight = 1.0,
      final Map<String, dynamic>? attributes})
      : _attributes = attributes;

  factory _$GraphEdgeImpl.fromJson(Map<String, dynamic> json) =>
      _$$GraphEdgeImplFromJson(json);

  @override
  final String source;
  @override
  final String target;
  @override
  final String? edgeType;
  @override
  @JsonKey()
  final double weight;
  final Map<String, dynamic>? _attributes;
  @override
  Map<String, dynamic>? get attributes {
    final value = _attributes;
    if (value == null) return null;
    if (_attributes is EqualUnmodifiableMapView) return _attributes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'GraphEdge(source: $source, target: $target, edgeType: $edgeType, weight: $weight, attributes: $attributes)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'GraphEdge'))
      ..add(DiagnosticsProperty('source', source))
      ..add(DiagnosticsProperty('target', target))
      ..add(DiagnosticsProperty('edgeType', edgeType))
      ..add(DiagnosticsProperty('weight', weight))
      ..add(DiagnosticsProperty('attributes', attributes));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$GraphEdgeImpl &&
            (identical(other.source, source) || other.source == source) &&
            (identical(other.target, target) || other.target == target) &&
            (identical(other.edgeType, edgeType) ||
                other.edgeType == edgeType) &&
            (identical(other.weight, weight) || other.weight == weight) &&
            const DeepCollectionEquality()
                .equals(other._attributes, _attributes));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, source, target, edgeType, weight,
      const DeepCollectionEquality().hash(_attributes));

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$GraphEdgeImplCopyWith<_$GraphEdgeImpl> get copyWith =>
      __$$GraphEdgeImplCopyWithImpl<_$GraphEdgeImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$GraphEdgeImplToJson(
      this,
    );
  }
}

abstract class _GraphEdge implements GraphEdge {
  const factory _GraphEdge(
      {required final String source,
      required final String target,
      final String? edgeType,
      final double weight,
      final Map<String, dynamic>? attributes}) = _$GraphEdgeImpl;

  factory _GraphEdge.fromJson(Map<String, dynamic> json) =
      _$GraphEdgeImpl.fromJson;

  @override
  String get source;
  @override
  String get target;
  @override
  String? get edgeType;
  @override
  double get weight;
  @override
  Map<String, dynamic>? get attributes;

  /// Create a copy of GraphEdge
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$GraphEdgeImplCopyWith<_$GraphEdgeImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

UnifiedGraphData _$UnifiedGraphDataFromJson(Map<String, dynamic> json) {
  return _UnifiedGraphData.fromJson(json);
}

/// @nodoc
mixin _$UnifiedGraphData {
  List<GraphNode> get nodes => throw _privateConstructorUsedError;
  List<GraphEdge> get edges => throw _privateConstructorUsedError;
  Map<String, dynamic>? get graphAttributes =>
      throw _privateConstructorUsedError;
  String? get graphType => throw _privateConstructorUsedError;
  bool get isDirected => throw _privateConstructorUsedError;
  DateTime get lastUpdated => throw _privateConstructorUsedError;
  Map<String, List<String>>? get clusters => throw _privateConstructorUsedError;
  Map<String, double>? get centrality => throw _privateConstructorUsedError;

  /// Serializes this UnifiedGraphData to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UnifiedGraphData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UnifiedGraphDataCopyWith<UnifiedGraphData> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UnifiedGraphDataCopyWith<$Res> {
  factory $UnifiedGraphDataCopyWith(
          UnifiedGraphData value, $Res Function(UnifiedGraphData) then) =
      _$UnifiedGraphDataCopyWithImpl<$Res, UnifiedGraphData>;
  @useResult
  $Res call(
      {List<GraphNode> nodes,
      List<GraphEdge> edges,
      Map<String, dynamic>? graphAttributes,
      String? graphType,
      bool isDirected,
      DateTime lastUpdated,
      Map<String, List<String>>? clusters,
      Map<String, double>? centrality});
}

/// @nodoc
class _$UnifiedGraphDataCopyWithImpl<$Res, $Val extends UnifiedGraphData>
    implements $UnifiedGraphDataCopyWith<$Res> {
  _$UnifiedGraphDataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UnifiedGraphData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? nodes = null,
    Object? edges = null,
    Object? graphAttributes = freezed,
    Object? graphType = freezed,
    Object? isDirected = null,
    Object? lastUpdated = null,
    Object? clusters = freezed,
    Object? centrality = freezed,
  }) {
    return _then(_value.copyWith(
      nodes: null == nodes
          ? _value.nodes
          : nodes // ignore: cast_nullable_to_non_nullable
              as List<GraphNode>,
      edges: null == edges
          ? _value.edges
          : edges // ignore: cast_nullable_to_non_nullable
              as List<GraphEdge>,
      graphAttributes: freezed == graphAttributes
          ? _value.graphAttributes
          : graphAttributes // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      graphType: freezed == graphType
          ? _value.graphType
          : graphType // ignore: cast_nullable_to_non_nullable
              as String?,
      isDirected: null == isDirected
          ? _value.isDirected
          : isDirected // ignore: cast_nullable_to_non_nullable
              as bool,
      lastUpdated: null == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime,
      clusters: freezed == clusters
          ? _value.clusters
          : clusters // ignore: cast_nullable_to_non_nullable
              as Map<String, List<String>>?,
      centrality: freezed == centrality
          ? _value.centrality
          : centrality // ignore: cast_nullable_to_non_nullable
              as Map<String, double>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UnifiedGraphDataImplCopyWith<$Res>
    implements $UnifiedGraphDataCopyWith<$Res> {
  factory _$$UnifiedGraphDataImplCopyWith(_$UnifiedGraphDataImpl value,
          $Res Function(_$UnifiedGraphDataImpl) then) =
      __$$UnifiedGraphDataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<GraphNode> nodes,
      List<GraphEdge> edges,
      Map<String, dynamic>? graphAttributes,
      String? graphType,
      bool isDirected,
      DateTime lastUpdated,
      Map<String, List<String>>? clusters,
      Map<String, double>? centrality});
}

/// @nodoc
class __$$UnifiedGraphDataImplCopyWithImpl<$Res>
    extends _$UnifiedGraphDataCopyWithImpl<$Res, _$UnifiedGraphDataImpl>
    implements _$$UnifiedGraphDataImplCopyWith<$Res> {
  __$$UnifiedGraphDataImplCopyWithImpl(_$UnifiedGraphDataImpl _value,
      $Res Function(_$UnifiedGraphDataImpl) _then)
      : super(_value, _then);

  /// Create a copy of UnifiedGraphData
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? nodes = null,
    Object? edges = null,
    Object? graphAttributes = freezed,
    Object? graphType = freezed,
    Object? isDirected = null,
    Object? lastUpdated = null,
    Object? clusters = freezed,
    Object? centrality = freezed,
  }) {
    return _then(_$UnifiedGraphDataImpl(
      nodes: null == nodes
          ? _value._nodes
          : nodes // ignore: cast_nullable_to_non_nullable
              as List<GraphNode>,
      edges: null == edges
          ? _value._edges
          : edges // ignore: cast_nullable_to_non_nullable
              as List<GraphEdge>,
      graphAttributes: freezed == graphAttributes
          ? _value._graphAttributes
          : graphAttributes // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      graphType: freezed == graphType
          ? _value.graphType
          : graphType // ignore: cast_nullable_to_non_nullable
              as String?,
      isDirected: null == isDirected
          ? _value.isDirected
          : isDirected // ignore: cast_nullable_to_non_nullable
              as bool,
      lastUpdated: null == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime,
      clusters: freezed == clusters
          ? _value._clusters
          : clusters // ignore: cast_nullable_to_non_nullable
              as Map<String, List<String>>?,
      centrality: freezed == centrality
          ? _value._centrality
          : centrality // ignore: cast_nullable_to_non_nullable
              as Map<String, double>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UnifiedGraphDataImpl
    with DiagnosticableTreeMixin
    implements _UnifiedGraphData {
  const _$UnifiedGraphDataImpl(
      {required final List<GraphNode> nodes,
      required final List<GraphEdge> edges,
      final Map<String, dynamic>? graphAttributes,
      this.graphType,
      this.isDirected = false,
      required this.lastUpdated,
      final Map<String, List<String>>? clusters,
      final Map<String, double>? centrality})
      : _nodes = nodes,
        _edges = edges,
        _graphAttributes = graphAttributes,
        _clusters = clusters,
        _centrality = centrality;

  factory _$UnifiedGraphDataImpl.fromJson(Map<String, dynamic> json) =>
      _$$UnifiedGraphDataImplFromJson(json);

  final List<GraphNode> _nodes;
  @override
  List<GraphNode> get nodes {
    if (_nodes is EqualUnmodifiableListView) return _nodes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_nodes);
  }

  final List<GraphEdge> _edges;
  @override
  List<GraphEdge> get edges {
    if (_edges is EqualUnmodifiableListView) return _edges;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_edges);
  }

  final Map<String, dynamic>? _graphAttributes;
  @override
  Map<String, dynamic>? get graphAttributes {
    final value = _graphAttributes;
    if (value == null) return null;
    if (_graphAttributes is EqualUnmodifiableMapView) return _graphAttributes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final String? graphType;
  @override
  @JsonKey()
  final bool isDirected;
  @override
  final DateTime lastUpdated;
  final Map<String, List<String>>? _clusters;
  @override
  Map<String, List<String>>? get clusters {
    final value = _clusters;
    if (value == null) return null;
    if (_clusters is EqualUnmodifiableMapView) return _clusters;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, double>? _centrality;
  @override
  Map<String, double>? get centrality {
    final value = _centrality;
    if (value == null) return null;
    if (_centrality is EqualUnmodifiableMapView) return _centrality;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'UnifiedGraphData(nodes: $nodes, edges: $edges, graphAttributes: $graphAttributes, graphType: $graphType, isDirected: $isDirected, lastUpdated: $lastUpdated, clusters: $clusters, centrality: $centrality)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'UnifiedGraphData'))
      ..add(DiagnosticsProperty('nodes', nodes))
      ..add(DiagnosticsProperty('edges', edges))
      ..add(DiagnosticsProperty('graphAttributes', graphAttributes))
      ..add(DiagnosticsProperty('graphType', graphType))
      ..add(DiagnosticsProperty('isDirected', isDirected))
      ..add(DiagnosticsProperty('lastUpdated', lastUpdated))
      ..add(DiagnosticsProperty('clusters', clusters))
      ..add(DiagnosticsProperty('centrality', centrality));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UnifiedGraphDataImpl &&
            const DeepCollectionEquality().equals(other._nodes, _nodes) &&
            const DeepCollectionEquality().equals(other._edges, _edges) &&
            const DeepCollectionEquality()
                .equals(other._graphAttributes, _graphAttributes) &&
            (identical(other.graphType, graphType) ||
                other.graphType == graphType) &&
            (identical(other.isDirected, isDirected) ||
                other.isDirected == isDirected) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated) &&
            const DeepCollectionEquality().equals(other._clusters, _clusters) &&
            const DeepCollectionEquality()
                .equals(other._centrality, _centrality));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_nodes),
      const DeepCollectionEquality().hash(_edges),
      const DeepCollectionEquality().hash(_graphAttributes),
      graphType,
      isDirected,
      lastUpdated,
      const DeepCollectionEquality().hash(_clusters),
      const DeepCollectionEquality().hash(_centrality));

  /// Create a copy of UnifiedGraphData
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UnifiedGraphDataImplCopyWith<_$UnifiedGraphDataImpl> get copyWith =>
      __$$UnifiedGraphDataImplCopyWithImpl<_$UnifiedGraphDataImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UnifiedGraphDataImplToJson(
      this,
    );
  }
}

abstract class _UnifiedGraphData implements UnifiedGraphData {
  const factory _UnifiedGraphData(
      {required final List<GraphNode> nodes,
      required final List<GraphEdge> edges,
      final Map<String, dynamic>? graphAttributes,
      final String? graphType,
      final bool isDirected,
      required final DateTime lastUpdated,
      final Map<String, List<String>>? clusters,
      final Map<String, double>? centrality}) = _$UnifiedGraphDataImpl;

  factory _UnifiedGraphData.fromJson(Map<String, dynamic> json) =
      _$UnifiedGraphDataImpl.fromJson;

  @override
  List<GraphNode> get nodes;
  @override
  List<GraphEdge> get edges;
  @override
  Map<String, dynamic>? get graphAttributes;
  @override
  String? get graphType;
  @override
  bool get isDirected;
  @override
  DateTime get lastUpdated;
  @override
  Map<String, List<String>>? get clusters;
  @override
  Map<String, double>? get centrality;

  /// Create a copy of UnifiedGraphData
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UnifiedGraphDataImplCopyWith<_$UnifiedGraphDataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

UnifiedVectorDocument _$UnifiedVectorDocumentFromJson(
    Map<String, dynamic> json) {
  return _UnifiedVectorDocument.fromJson(json);
}

/// @nodoc
mixin _$UnifiedVectorDocument {
  String get documentId => throw _privateConstructorUsedError;
  String get content => throw _privateConstructorUsedError;
  String? get title => throw _privateConstructorUsedError;
  String? get contentType => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;
  List<double> get embedding => throw _privateConstructorUsedError;
  double get score => throw _privateConstructorUsedError;
  String? get sourceConnector => throw _privateConstructorUsedError;
  String? get sourcePath => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;

  /// Serializes this UnifiedVectorDocument to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UnifiedVectorDocument
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UnifiedVectorDocumentCopyWith<UnifiedVectorDocument> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UnifiedVectorDocumentCopyWith<$Res> {
  factory $UnifiedVectorDocumentCopyWith(UnifiedVectorDocument value,
          $Res Function(UnifiedVectorDocument) then) =
      _$UnifiedVectorDocumentCopyWithImpl<$Res, UnifiedVectorDocument>;
  @useResult
  $Res call(
      {String documentId,
      String content,
      String? title,
      String? contentType,
      Map<String, dynamic>? metadata,
      List<double> embedding,
      double score,
      String? sourceConnector,
      String? sourcePath,
      DateTime timestamp});
}

/// @nodoc
class _$UnifiedVectorDocumentCopyWithImpl<$Res,
        $Val extends UnifiedVectorDocument>
    implements $UnifiedVectorDocumentCopyWith<$Res> {
  _$UnifiedVectorDocumentCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UnifiedVectorDocument
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? documentId = null,
    Object? content = null,
    Object? title = freezed,
    Object? contentType = freezed,
    Object? metadata = freezed,
    Object? embedding = null,
    Object? score = null,
    Object? sourceConnector = freezed,
    Object? sourcePath = freezed,
    Object? timestamp = null,
  }) {
    return _then(_value.copyWith(
      documentId: null == documentId
          ? _value.documentId
          : documentId // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      title: freezed == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String?,
      contentType: freezed == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      embedding: null == embedding
          ? _value.embedding
          : embedding // ignore: cast_nullable_to_non_nullable
              as List<double>,
      score: null == score
          ? _value.score
          : score // ignore: cast_nullable_to_non_nullable
              as double,
      sourceConnector: freezed == sourceConnector
          ? _value.sourceConnector
          : sourceConnector // ignore: cast_nullable_to_non_nullable
              as String?,
      sourcePath: freezed == sourcePath
          ? _value.sourcePath
          : sourcePath // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UnifiedVectorDocumentImplCopyWith<$Res>
    implements $UnifiedVectorDocumentCopyWith<$Res> {
  factory _$$UnifiedVectorDocumentImplCopyWith(
          _$UnifiedVectorDocumentImpl value,
          $Res Function(_$UnifiedVectorDocumentImpl) then) =
      __$$UnifiedVectorDocumentImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String documentId,
      String content,
      String? title,
      String? contentType,
      Map<String, dynamic>? metadata,
      List<double> embedding,
      double score,
      String? sourceConnector,
      String? sourcePath,
      DateTime timestamp});
}

/// @nodoc
class __$$UnifiedVectorDocumentImplCopyWithImpl<$Res>
    extends _$UnifiedVectorDocumentCopyWithImpl<$Res,
        _$UnifiedVectorDocumentImpl>
    implements _$$UnifiedVectorDocumentImplCopyWith<$Res> {
  __$$UnifiedVectorDocumentImplCopyWithImpl(_$UnifiedVectorDocumentImpl _value,
      $Res Function(_$UnifiedVectorDocumentImpl) _then)
      : super(_value, _then);

  /// Create a copy of UnifiedVectorDocument
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? documentId = null,
    Object? content = null,
    Object? title = freezed,
    Object? contentType = freezed,
    Object? metadata = freezed,
    Object? embedding = null,
    Object? score = null,
    Object? sourceConnector = freezed,
    Object? sourcePath = freezed,
    Object? timestamp = null,
  }) {
    return _then(_$UnifiedVectorDocumentImpl(
      documentId: null == documentId
          ? _value.documentId
          : documentId // ignore: cast_nullable_to_non_nullable
              as String,
      content: null == content
          ? _value.content
          : content // ignore: cast_nullable_to_non_nullable
              as String,
      title: freezed == title
          ? _value.title
          : title // ignore: cast_nullable_to_non_nullable
              as String?,
      contentType: freezed == contentType
          ? _value.contentType
          : contentType // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      embedding: null == embedding
          ? _value._embedding
          : embedding // ignore: cast_nullable_to_non_nullable
              as List<double>,
      score: null == score
          ? _value.score
          : score // ignore: cast_nullable_to_non_nullable
              as double,
      sourceConnector: freezed == sourceConnector
          ? _value.sourceConnector
          : sourceConnector // ignore: cast_nullable_to_non_nullable
              as String?,
      sourcePath: freezed == sourcePath
          ? _value.sourcePath
          : sourcePath // ignore: cast_nullable_to_non_nullable
              as String?,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UnifiedVectorDocumentImpl
    with DiagnosticableTreeMixin
    implements _UnifiedVectorDocument {
  const _$UnifiedVectorDocumentImpl(
      {required this.documentId,
      required this.content,
      this.title,
      this.contentType,
      final Map<String, dynamic>? metadata,
      required final List<double> embedding,
      this.score = 0.0,
      this.sourceConnector,
      this.sourcePath,
      required this.timestamp})
      : _metadata = metadata,
        _embedding = embedding;

  factory _$UnifiedVectorDocumentImpl.fromJson(Map<String, dynamic> json) =>
      _$$UnifiedVectorDocumentImplFromJson(json);

  @override
  final String documentId;
  @override
  final String content;
  @override
  final String? title;
  @override
  final String? contentType;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final List<double> _embedding;
  @override
  List<double> get embedding {
    if (_embedding is EqualUnmodifiableListView) return _embedding;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_embedding);
  }

  @override
  @JsonKey()
  final double score;
  @override
  final String? sourceConnector;
  @override
  final String? sourcePath;
  @override
  final DateTime timestamp;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'UnifiedVectorDocument(documentId: $documentId, content: $content, title: $title, contentType: $contentType, metadata: $metadata, embedding: $embedding, score: $score, sourceConnector: $sourceConnector, sourcePath: $sourcePath, timestamp: $timestamp)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'UnifiedVectorDocument'))
      ..add(DiagnosticsProperty('documentId', documentId))
      ..add(DiagnosticsProperty('content', content))
      ..add(DiagnosticsProperty('title', title))
      ..add(DiagnosticsProperty('contentType', contentType))
      ..add(DiagnosticsProperty('metadata', metadata))
      ..add(DiagnosticsProperty('embedding', embedding))
      ..add(DiagnosticsProperty('score', score))
      ..add(DiagnosticsProperty('sourceConnector', sourceConnector))
      ..add(DiagnosticsProperty('sourcePath', sourcePath))
      ..add(DiagnosticsProperty('timestamp', timestamp));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UnifiedVectorDocumentImpl &&
            (identical(other.documentId, documentId) ||
                other.documentId == documentId) &&
            (identical(other.content, content) || other.content == content) &&
            (identical(other.title, title) || other.title == title) &&
            (identical(other.contentType, contentType) ||
                other.contentType == contentType) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            const DeepCollectionEquality()
                .equals(other._embedding, _embedding) &&
            (identical(other.score, score) || other.score == score) &&
            (identical(other.sourceConnector, sourceConnector) ||
                other.sourceConnector == sourceConnector) &&
            (identical(other.sourcePath, sourcePath) ||
                other.sourcePath == sourcePath) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      documentId,
      content,
      title,
      contentType,
      const DeepCollectionEquality().hash(_metadata),
      const DeepCollectionEquality().hash(_embedding),
      score,
      sourceConnector,
      sourcePath,
      timestamp);

  /// Create a copy of UnifiedVectorDocument
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UnifiedVectorDocumentImplCopyWith<_$UnifiedVectorDocumentImpl>
      get copyWith => __$$UnifiedVectorDocumentImplCopyWithImpl<
          _$UnifiedVectorDocumentImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UnifiedVectorDocumentImplToJson(
      this,
    );
  }
}

abstract class _UnifiedVectorDocument implements UnifiedVectorDocument {
  const factory _UnifiedVectorDocument(
      {required final String documentId,
      required final String content,
      final String? title,
      final String? contentType,
      final Map<String, dynamic>? metadata,
      required final List<double> embedding,
      final double score,
      final String? sourceConnector,
      final String? sourcePath,
      required final DateTime timestamp}) = _$UnifiedVectorDocumentImpl;

  factory _UnifiedVectorDocument.fromJson(Map<String, dynamic> json) =
      _$UnifiedVectorDocumentImpl.fromJson;

  @override
  String get documentId;
  @override
  String get content;
  @override
  String? get title;
  @override
  String? get contentType;
  @override
  Map<String, dynamic>? get metadata;
  @override
  List<double> get embedding;
  @override
  double get score;
  @override
  String? get sourceConnector;
  @override
  String? get sourcePath;
  @override
  DateTime get timestamp;

  /// Create a copy of UnifiedVectorDocument
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UnifiedVectorDocumentImplCopyWith<_$UnifiedVectorDocumentImpl>
      get copyWith => throw _privateConstructorUsedError;
}

VectorSearchResult _$VectorSearchResultFromJson(Map<String, dynamic> json) {
  return _VectorSearchResult.fromJson(json);
}

/// @nodoc
mixin _$VectorSearchResult {
  String get query => throw _privateConstructorUsedError;
  List<double> get queryEmbedding => throw _privateConstructorUsedError;
  List<UnifiedVectorDocument> get results => throw _privateConstructorUsedError;
  int get totalCount => throw _privateConstructorUsedError;
  Duration get searchTime => throw _privateConstructorUsedError;
  String get similarityMetric => throw _privateConstructorUsedError;

  /// Serializes this VectorSearchResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of VectorSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $VectorSearchResultCopyWith<VectorSearchResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VectorSearchResultCopyWith<$Res> {
  factory $VectorSearchResultCopyWith(
          VectorSearchResult value, $Res Function(VectorSearchResult) then) =
      _$VectorSearchResultCopyWithImpl<$Res, VectorSearchResult>;
  @useResult
  $Res call(
      {String query,
      List<double> queryEmbedding,
      List<UnifiedVectorDocument> results,
      int totalCount,
      Duration searchTime,
      String similarityMetric});
}

/// @nodoc
class _$VectorSearchResultCopyWithImpl<$Res, $Val extends VectorSearchResult>
    implements $VectorSearchResultCopyWith<$Res> {
  _$VectorSearchResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of VectorSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? query = null,
    Object? queryEmbedding = null,
    Object? results = null,
    Object? totalCount = null,
    Object? searchTime = null,
    Object? similarityMetric = null,
  }) {
    return _then(_value.copyWith(
      query: null == query
          ? _value.query
          : query // ignore: cast_nullable_to_non_nullable
              as String,
      queryEmbedding: null == queryEmbedding
          ? _value.queryEmbedding
          : queryEmbedding // ignore: cast_nullable_to_non_nullable
              as List<double>,
      results: null == results
          ? _value.results
          : results // ignore: cast_nullable_to_non_nullable
              as List<UnifiedVectorDocument>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      searchTime: null == searchTime
          ? _value.searchTime
          : searchTime // ignore: cast_nullable_to_non_nullable
              as Duration,
      similarityMetric: null == similarityMetric
          ? _value.similarityMetric
          : similarityMetric // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VectorSearchResultImplCopyWith<$Res>
    implements $VectorSearchResultCopyWith<$Res> {
  factory _$$VectorSearchResultImplCopyWith(_$VectorSearchResultImpl value,
          $Res Function(_$VectorSearchResultImpl) then) =
      __$$VectorSearchResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String query,
      List<double> queryEmbedding,
      List<UnifiedVectorDocument> results,
      int totalCount,
      Duration searchTime,
      String similarityMetric});
}

/// @nodoc
class __$$VectorSearchResultImplCopyWithImpl<$Res>
    extends _$VectorSearchResultCopyWithImpl<$Res, _$VectorSearchResultImpl>
    implements _$$VectorSearchResultImplCopyWith<$Res> {
  __$$VectorSearchResultImplCopyWithImpl(_$VectorSearchResultImpl _value,
      $Res Function(_$VectorSearchResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of VectorSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? query = null,
    Object? queryEmbedding = null,
    Object? results = null,
    Object? totalCount = null,
    Object? searchTime = null,
    Object? similarityMetric = null,
  }) {
    return _then(_$VectorSearchResultImpl(
      query: null == query
          ? _value.query
          : query // ignore: cast_nullable_to_non_nullable
              as String,
      queryEmbedding: null == queryEmbedding
          ? _value._queryEmbedding
          : queryEmbedding // ignore: cast_nullable_to_non_nullable
              as List<double>,
      results: null == results
          ? _value._results
          : results // ignore: cast_nullable_to_non_nullable
              as List<UnifiedVectorDocument>,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      searchTime: null == searchTime
          ? _value.searchTime
          : searchTime // ignore: cast_nullable_to_non_nullable
              as Duration,
      similarityMetric: null == similarityMetric
          ? _value.similarityMetric
          : similarityMetric // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VectorSearchResultImpl
    with DiagnosticableTreeMixin
    implements _VectorSearchResult {
  const _$VectorSearchResultImpl(
      {required this.query,
      required final List<double> queryEmbedding,
      required final List<UnifiedVectorDocument> results,
      required this.totalCount,
      required this.searchTime,
      this.similarityMetric = 'cosine'})
      : _queryEmbedding = queryEmbedding,
        _results = results;

  factory _$VectorSearchResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$VectorSearchResultImplFromJson(json);

  @override
  final String query;
  final List<double> _queryEmbedding;
  @override
  List<double> get queryEmbedding {
    if (_queryEmbedding is EqualUnmodifiableListView) return _queryEmbedding;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_queryEmbedding);
  }

  final List<UnifiedVectorDocument> _results;
  @override
  List<UnifiedVectorDocument> get results {
    if (_results is EqualUnmodifiableListView) return _results;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_results);
  }

  @override
  final int totalCount;
  @override
  final Duration searchTime;
  @override
  @JsonKey()
  final String similarityMetric;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'VectorSearchResult(query: $query, queryEmbedding: $queryEmbedding, results: $results, totalCount: $totalCount, searchTime: $searchTime, similarityMetric: $similarityMetric)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'VectorSearchResult'))
      ..add(DiagnosticsProperty('query', query))
      ..add(DiagnosticsProperty('queryEmbedding', queryEmbedding))
      ..add(DiagnosticsProperty('results', results))
      ..add(DiagnosticsProperty('totalCount', totalCount))
      ..add(DiagnosticsProperty('searchTime', searchTime))
      ..add(DiagnosticsProperty('similarityMetric', similarityMetric));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VectorSearchResultImpl &&
            (identical(other.query, query) || other.query == query) &&
            const DeepCollectionEquality()
                .equals(other._queryEmbedding, _queryEmbedding) &&
            const DeepCollectionEquality().equals(other._results, _results) &&
            (identical(other.totalCount, totalCount) ||
                other.totalCount == totalCount) &&
            (identical(other.searchTime, searchTime) ||
                other.searchTime == searchTime) &&
            (identical(other.similarityMetric, similarityMetric) ||
                other.similarityMetric == similarityMetric));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      query,
      const DeepCollectionEquality().hash(_queryEmbedding),
      const DeepCollectionEquality().hash(_results),
      totalCount,
      searchTime,
      similarityMetric);

  /// Create a copy of VectorSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$VectorSearchResultImplCopyWith<_$VectorSearchResultImpl> get copyWith =>
      __$$VectorSearchResultImplCopyWithImpl<_$VectorSearchResultImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VectorSearchResultImplToJson(
      this,
    );
  }
}

abstract class _VectorSearchResult implements VectorSearchResult {
  const factory _VectorSearchResult(
      {required final String query,
      required final List<double> queryEmbedding,
      required final List<UnifiedVectorDocument> results,
      required final int totalCount,
      required final Duration searchTime,
      final String similarityMetric}) = _$VectorSearchResultImpl;

  factory _VectorSearchResult.fromJson(Map<String, dynamic> json) =
      _$VectorSearchResultImpl.fromJson;

  @override
  String get query;
  @override
  List<double> get queryEmbedding;
  @override
  List<UnifiedVectorDocument> get results;
  @override
  int get totalCount;
  @override
  Duration get searchTime;
  @override
  String get similarityMetric;

  /// Create a copy of VectorSearchResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$VectorSearchResultImplCopyWith<_$VectorSearchResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

VectorCluster _$VectorClusterFromJson(Map<String, dynamic> json) {
  return _VectorCluster.fromJson(json);
}

/// @nodoc
mixin _$VectorCluster {
  String get clusterId => throw _privateConstructorUsedError;
  List<String> get documentIds => throw _privateConstructorUsedError;
  List<double> get centroid => throw _privateConstructorUsedError;
  double get cohesion => throw _privateConstructorUsedError;
  String? get topic => throw _privateConstructorUsedError;
  List<String>? get keywords => throw _privateConstructorUsedError;

  /// Serializes this VectorCluster to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of VectorCluster
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $VectorClusterCopyWith<VectorCluster> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VectorClusterCopyWith<$Res> {
  factory $VectorClusterCopyWith(
          VectorCluster value, $Res Function(VectorCluster) then) =
      _$VectorClusterCopyWithImpl<$Res, VectorCluster>;
  @useResult
  $Res call(
      {String clusterId,
      List<String> documentIds,
      List<double> centroid,
      double cohesion,
      String? topic,
      List<String>? keywords});
}

/// @nodoc
class _$VectorClusterCopyWithImpl<$Res, $Val extends VectorCluster>
    implements $VectorClusterCopyWith<$Res> {
  _$VectorClusterCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of VectorCluster
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? clusterId = null,
    Object? documentIds = null,
    Object? centroid = null,
    Object? cohesion = null,
    Object? topic = freezed,
    Object? keywords = freezed,
  }) {
    return _then(_value.copyWith(
      clusterId: null == clusterId
          ? _value.clusterId
          : clusterId // ignore: cast_nullable_to_non_nullable
              as String,
      documentIds: null == documentIds
          ? _value.documentIds
          : documentIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
      centroid: null == centroid
          ? _value.centroid
          : centroid // ignore: cast_nullable_to_non_nullable
              as List<double>,
      cohesion: null == cohesion
          ? _value.cohesion
          : cohesion // ignore: cast_nullable_to_non_nullable
              as double,
      topic: freezed == topic
          ? _value.topic
          : topic // ignore: cast_nullable_to_non_nullable
              as String?,
      keywords: freezed == keywords
          ? _value.keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VectorClusterImplCopyWith<$Res>
    implements $VectorClusterCopyWith<$Res> {
  factory _$$VectorClusterImplCopyWith(
          _$VectorClusterImpl value, $Res Function(_$VectorClusterImpl) then) =
      __$$VectorClusterImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String clusterId,
      List<String> documentIds,
      List<double> centroid,
      double cohesion,
      String? topic,
      List<String>? keywords});
}

/// @nodoc
class __$$VectorClusterImplCopyWithImpl<$Res>
    extends _$VectorClusterCopyWithImpl<$Res, _$VectorClusterImpl>
    implements _$$VectorClusterImplCopyWith<$Res> {
  __$$VectorClusterImplCopyWithImpl(
      _$VectorClusterImpl _value, $Res Function(_$VectorClusterImpl) _then)
      : super(_value, _then);

  /// Create a copy of VectorCluster
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? clusterId = null,
    Object? documentIds = null,
    Object? centroid = null,
    Object? cohesion = null,
    Object? topic = freezed,
    Object? keywords = freezed,
  }) {
    return _then(_$VectorClusterImpl(
      clusterId: null == clusterId
          ? _value.clusterId
          : clusterId // ignore: cast_nullable_to_non_nullable
              as String,
      documentIds: null == documentIds
          ? _value._documentIds
          : documentIds // ignore: cast_nullable_to_non_nullable
              as List<String>,
      centroid: null == centroid
          ? _value._centroid
          : centroid // ignore: cast_nullable_to_non_nullable
              as List<double>,
      cohesion: null == cohesion
          ? _value.cohesion
          : cohesion // ignore: cast_nullable_to_non_nullable
              as double,
      topic: freezed == topic
          ? _value.topic
          : topic // ignore: cast_nullable_to_non_nullable
              as String?,
      keywords: freezed == keywords
          ? _value._keywords
          : keywords // ignore: cast_nullable_to_non_nullable
              as List<String>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VectorClusterImpl
    with DiagnosticableTreeMixin
    implements _VectorCluster {
  const _$VectorClusterImpl(
      {required this.clusterId,
      required final List<String> documentIds,
      required final List<double> centroid,
      this.cohesion = 0.0,
      this.topic,
      final List<String>? keywords})
      : _documentIds = documentIds,
        _centroid = centroid,
        _keywords = keywords;

  factory _$VectorClusterImpl.fromJson(Map<String, dynamic> json) =>
      _$$VectorClusterImplFromJson(json);

  @override
  final String clusterId;
  final List<String> _documentIds;
  @override
  List<String> get documentIds {
    if (_documentIds is EqualUnmodifiableListView) return _documentIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_documentIds);
  }

  final List<double> _centroid;
  @override
  List<double> get centroid {
    if (_centroid is EqualUnmodifiableListView) return _centroid;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_centroid);
  }

  @override
  @JsonKey()
  final double cohesion;
  @override
  final String? topic;
  final List<String>? _keywords;
  @override
  List<String>? get keywords {
    final value = _keywords;
    if (value == null) return null;
    if (_keywords is EqualUnmodifiableListView) return _keywords;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'VectorCluster(clusterId: $clusterId, documentIds: $documentIds, centroid: $centroid, cohesion: $cohesion, topic: $topic, keywords: $keywords)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'VectorCluster'))
      ..add(DiagnosticsProperty('clusterId', clusterId))
      ..add(DiagnosticsProperty('documentIds', documentIds))
      ..add(DiagnosticsProperty('centroid', centroid))
      ..add(DiagnosticsProperty('cohesion', cohesion))
      ..add(DiagnosticsProperty('topic', topic))
      ..add(DiagnosticsProperty('keywords', keywords));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VectorClusterImpl &&
            (identical(other.clusterId, clusterId) ||
                other.clusterId == clusterId) &&
            const DeepCollectionEquality()
                .equals(other._documentIds, _documentIds) &&
            const DeepCollectionEquality().equals(other._centroid, _centroid) &&
            (identical(other.cohesion, cohesion) ||
                other.cohesion == cohesion) &&
            (identical(other.topic, topic) || other.topic == topic) &&
            const DeepCollectionEquality().equals(other._keywords, _keywords));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      clusterId,
      const DeepCollectionEquality().hash(_documentIds),
      const DeepCollectionEquality().hash(_centroid),
      cohesion,
      topic,
      const DeepCollectionEquality().hash(_keywords));

  /// Create a copy of VectorCluster
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$VectorClusterImplCopyWith<_$VectorClusterImpl> get copyWith =>
      __$$VectorClusterImplCopyWithImpl<_$VectorClusterImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VectorClusterImplToJson(
      this,
    );
  }
}

abstract class _VectorCluster implements VectorCluster {
  const factory _VectorCluster(
      {required final String clusterId,
      required final List<String> documentIds,
      required final List<double> centroid,
      final double cohesion,
      final String? topic,
      final List<String>? keywords}) = _$VectorClusterImpl;

  factory _VectorCluster.fromJson(Map<String, dynamic> json) =
      _$VectorClusterImpl.fromJson;

  @override
  String get clusterId;
  @override
  List<String> get documentIds;
  @override
  List<double> get centroid;
  @override
  double get cohesion;
  @override
  String? get topic;
  @override
  List<String>? get keywords;

  /// Create a copy of VectorCluster
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$VectorClusterImplCopyWith<_$VectorClusterImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

UnifiedApiResponse _$UnifiedApiResponseFromJson(Map<String, dynamic> json) {
  return _UnifiedApiResponse.fromJson(json);
}

/// @nodoc
mixin _$UnifiedApiResponse {
  bool get success => throw _privateConstructorUsedError;
  Map<String, dynamic>? get data => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  String? get message => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;

  /// Serializes this UnifiedApiResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of UnifiedApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $UnifiedApiResponseCopyWith<UnifiedApiResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $UnifiedApiResponseCopyWith<$Res> {
  factory $UnifiedApiResponseCopyWith(
          UnifiedApiResponse value, $Res Function(UnifiedApiResponse) then) =
      _$UnifiedApiResponseCopyWithImpl<$Res, UnifiedApiResponse>;
  @useResult
  $Res call(
      {bool success,
      Map<String, dynamic>? data,
      String? error,
      String? message,
      Map<String, dynamic>? metadata,
      DateTime timestamp});
}

/// @nodoc
class _$UnifiedApiResponseCopyWithImpl<$Res, $Val extends UnifiedApiResponse>
    implements $UnifiedApiResponseCopyWith<$Res> {
  _$UnifiedApiResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of UnifiedApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = freezed,
    Object? error = freezed,
    Object? message = freezed,
    Object? metadata = freezed,
    Object? timestamp = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: freezed == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      message: freezed == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$UnifiedApiResponseImplCopyWith<$Res>
    implements $UnifiedApiResponseCopyWith<$Res> {
  factory _$$UnifiedApiResponseImplCopyWith(_$UnifiedApiResponseImpl value,
          $Res Function(_$UnifiedApiResponseImpl) then) =
      __$$UnifiedApiResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      Map<String, dynamic>? data,
      String? error,
      String? message,
      Map<String, dynamic>? metadata,
      DateTime timestamp});
}

/// @nodoc
class __$$UnifiedApiResponseImplCopyWithImpl<$Res>
    extends _$UnifiedApiResponseCopyWithImpl<$Res, _$UnifiedApiResponseImpl>
    implements _$$UnifiedApiResponseImplCopyWith<$Res> {
  __$$UnifiedApiResponseImplCopyWithImpl(_$UnifiedApiResponseImpl _value,
      $Res Function(_$UnifiedApiResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of UnifiedApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? data = freezed,
    Object? error = freezed,
    Object? message = freezed,
    Object? metadata = freezed,
    Object? timestamp = null,
  }) {
    return _then(_$UnifiedApiResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      data: freezed == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      message: freezed == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String?,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$UnifiedApiResponseImpl
    with DiagnosticableTreeMixin
    implements _UnifiedApiResponse {
  const _$UnifiedApiResponseImpl(
      {required this.success,
      final Map<String, dynamic>? data,
      this.error,
      this.message,
      final Map<String, dynamic>? metadata,
      required this.timestamp})
      : _data = data,
        _metadata = metadata;

  factory _$UnifiedApiResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$UnifiedApiResponseImplFromJson(json);

  @override
  final bool success;
  final Map<String, dynamic>? _data;
  @override
  Map<String, dynamic>? get data {
    final value = _data;
    if (value == null) return null;
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final String? error;
  @override
  final String? message;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final DateTime timestamp;

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'UnifiedApiResponse(success: $success, data: $data, error: $error, message: $message, metadata: $metadata, timestamp: $timestamp)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'UnifiedApiResponse'))
      ..add(DiagnosticsProperty('success', success))
      ..add(DiagnosticsProperty('data', data))
      ..add(DiagnosticsProperty('error', error))
      ..add(DiagnosticsProperty('message', message))
      ..add(DiagnosticsProperty('metadata', metadata))
      ..add(DiagnosticsProperty('timestamp', timestamp));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$UnifiedApiResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality().equals(other._data, _data) &&
            (identical(other.error, error) || other.error == error) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      const DeepCollectionEquality().hash(_data),
      error,
      message,
      const DeepCollectionEquality().hash(_metadata),
      timestamp);

  /// Create a copy of UnifiedApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$UnifiedApiResponseImplCopyWith<_$UnifiedApiResponseImpl> get copyWith =>
      __$$UnifiedApiResponseImplCopyWithImpl<_$UnifiedApiResponseImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$UnifiedApiResponseImplToJson(
      this,
    );
  }
}

abstract class _UnifiedApiResponse implements UnifiedApiResponse {
  const factory _UnifiedApiResponse(
      {required final bool success,
      final Map<String, dynamic>? data,
      final String? error,
      final String? message,
      final Map<String, dynamic>? metadata,
      required final DateTime timestamp}) = _$UnifiedApiResponseImpl;

  factory _UnifiedApiResponse.fromJson(Map<String, dynamic> json) =
      _$UnifiedApiResponseImpl.fromJson;

  @override
  bool get success;
  @override
  Map<String, dynamic>? get data;
  @override
  String? get error;
  @override
  String? get message;
  @override
  Map<String, dynamic>? get metadata;
  @override
  DateTime get timestamp;

  /// Create a copy of UnifiedApiResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$UnifiedApiResponseImplCopyWith<_$UnifiedApiResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DataSourceStats _$DataSourceStatsFromJson(Map<String, dynamic> json) {
  return _DataSourceStats.fromJson(json);
}

/// @nodoc
mixin _$DataSourceStats {
  String get dataType => throw _privateConstructorUsedError;
  int get totalCount => throw _privateConstructorUsedError;
  int get activeCount => throw _privateConstructorUsedError;
  DateTime get lastUpdated => throw _privateConstructorUsedError;
  Map<String, int>? get breakdown => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metrics => throw _privateConstructorUsedError;

  /// Serializes this DataSourceStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DataSourceStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DataSourceStatsCopyWith<DataSourceStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DataSourceStatsCopyWith<$Res> {
  factory $DataSourceStatsCopyWith(
          DataSourceStats value, $Res Function(DataSourceStats) then) =
      _$DataSourceStatsCopyWithImpl<$Res, DataSourceStats>;
  @useResult
  $Res call(
      {String dataType,
      int totalCount,
      int activeCount,
      DateTime lastUpdated,
      Map<String, int>? breakdown,
      Map<String, dynamic>? metrics});
}

/// @nodoc
class _$DataSourceStatsCopyWithImpl<$Res, $Val extends DataSourceStats>
    implements $DataSourceStatsCopyWith<$Res> {
  _$DataSourceStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DataSourceStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? dataType = null,
    Object? totalCount = null,
    Object? activeCount = null,
    Object? lastUpdated = null,
    Object? breakdown = freezed,
    Object? metrics = freezed,
  }) {
    return _then(_value.copyWith(
      dataType: null == dataType
          ? _value.dataType
          : dataType // ignore: cast_nullable_to_non_nullable
              as String,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      activeCount: null == activeCount
          ? _value.activeCount
          : activeCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastUpdated: null == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime,
      breakdown: freezed == breakdown
          ? _value.breakdown
          : breakdown // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
      metrics: freezed == metrics
          ? _value.metrics
          : metrics // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DataSourceStatsImplCopyWith<$Res>
    implements $DataSourceStatsCopyWith<$Res> {
  factory _$$DataSourceStatsImplCopyWith(_$DataSourceStatsImpl value,
          $Res Function(_$DataSourceStatsImpl) then) =
      __$$DataSourceStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String dataType,
      int totalCount,
      int activeCount,
      DateTime lastUpdated,
      Map<String, int>? breakdown,
      Map<String, dynamic>? metrics});
}

/// @nodoc
class __$$DataSourceStatsImplCopyWithImpl<$Res>
    extends _$DataSourceStatsCopyWithImpl<$Res, _$DataSourceStatsImpl>
    implements _$$DataSourceStatsImplCopyWith<$Res> {
  __$$DataSourceStatsImplCopyWithImpl(
      _$DataSourceStatsImpl _value, $Res Function(_$DataSourceStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of DataSourceStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? dataType = null,
    Object? totalCount = null,
    Object? activeCount = null,
    Object? lastUpdated = null,
    Object? breakdown = freezed,
    Object? metrics = freezed,
  }) {
    return _then(_$DataSourceStatsImpl(
      dataType: null == dataType
          ? _value.dataType
          : dataType // ignore: cast_nullable_to_non_nullable
              as String,
      totalCount: null == totalCount
          ? _value.totalCount
          : totalCount // ignore: cast_nullable_to_non_nullable
              as int,
      activeCount: null == activeCount
          ? _value.activeCount
          : activeCount // ignore: cast_nullable_to_non_nullable
              as int,
      lastUpdated: null == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime,
      breakdown: freezed == breakdown
          ? _value._breakdown
          : breakdown // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
      metrics: freezed == metrics
          ? _value._metrics
          : metrics // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DataSourceStatsImpl
    with DiagnosticableTreeMixin
    implements _DataSourceStats {
  const _$DataSourceStatsImpl(
      {required this.dataType,
      required this.totalCount,
      required this.activeCount,
      required this.lastUpdated,
      final Map<String, int>? breakdown,
      final Map<String, dynamic>? metrics})
      : _breakdown = breakdown,
        _metrics = metrics;

  factory _$DataSourceStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$DataSourceStatsImplFromJson(json);

  @override
  final String dataType;
  @override
  final int totalCount;
  @override
  final int activeCount;
  @override
  final DateTime lastUpdated;
  final Map<String, int>? _breakdown;
  @override
  Map<String, int>? get breakdown {
    final value = _breakdown;
    if (value == null) return null;
    if (_breakdown is EqualUnmodifiableMapView) return _breakdown;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, dynamic>? _metrics;
  @override
  Map<String, dynamic>? get metrics {
    final value = _metrics;
    if (value == null) return null;
    if (_metrics is EqualUnmodifiableMapView) return _metrics;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString({DiagnosticLevel minLevel = DiagnosticLevel.info}) {
    return 'DataSourceStats(dataType: $dataType, totalCount: $totalCount, activeCount: $activeCount, lastUpdated: $lastUpdated, breakdown: $breakdown, metrics: $metrics)';
  }

  @override
  void debugFillProperties(DiagnosticPropertiesBuilder properties) {
    super.debugFillProperties(properties);
    properties
      ..add(DiagnosticsProperty('type', 'DataSourceStats'))
      ..add(DiagnosticsProperty('dataType', dataType))
      ..add(DiagnosticsProperty('totalCount', totalCount))
      ..add(DiagnosticsProperty('activeCount', activeCount))
      ..add(DiagnosticsProperty('lastUpdated', lastUpdated))
      ..add(DiagnosticsProperty('breakdown', breakdown))
      ..add(DiagnosticsProperty('metrics', metrics));
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DataSourceStatsImpl &&
            (identical(other.dataType, dataType) ||
                other.dataType == dataType) &&
            (identical(other.totalCount, totalCount) ||
                other.totalCount == totalCount) &&
            (identical(other.activeCount, activeCount) ||
                other.activeCount == activeCount) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated) &&
            const DeepCollectionEquality()
                .equals(other._breakdown, _breakdown) &&
            const DeepCollectionEquality().equals(other._metrics, _metrics));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      dataType,
      totalCount,
      activeCount,
      lastUpdated,
      const DeepCollectionEquality().hash(_breakdown),
      const DeepCollectionEquality().hash(_metrics));

  /// Create a copy of DataSourceStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DataSourceStatsImplCopyWith<_$DataSourceStatsImpl> get copyWith =>
      __$$DataSourceStatsImplCopyWithImpl<_$DataSourceStatsImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DataSourceStatsImplToJson(
      this,
    );
  }
}

abstract class _DataSourceStats implements DataSourceStats {
  const factory _DataSourceStats(
      {required final String dataType,
      required final int totalCount,
      required final int activeCount,
      required final DateTime lastUpdated,
      final Map<String, int>? breakdown,
      final Map<String, dynamic>? metrics}) = _$DataSourceStatsImpl;

  factory _DataSourceStats.fromJson(Map<String, dynamic> json) =
      _$DataSourceStatsImpl.fromJson;

  @override
  String get dataType;
  @override
  int get totalCount;
  @override
  int get activeCount;
  @override
  DateTime get lastUpdated;
  @override
  Map<String, int>? get breakdown;
  @override
  Map<String, dynamic>? get metrics;

  /// Create a copy of DataSourceStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DataSourceStatsImplCopyWith<_$DataSourceStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
