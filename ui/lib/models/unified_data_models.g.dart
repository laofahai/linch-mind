// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'unified_data_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$UniversalIndexEntryImpl _$$UniversalIndexEntryImplFromJson(
        Map<String, dynamic> json) =>
    _$UniversalIndexEntryImpl(
      id: json['id'] as String,
      connectorId: json['connectorId'] as String,
      contentType:
          $enumDecode(_$UniversalContentTypeEnumMap, json['contentType']),
      primaryKey: json['primaryKey'] as String,
      searchableText: json['searchableText'] as String,
      displayName: json['displayName'] as String,
      indexTier: $enumDecode(_$IndexTierEnumMap, json['indexTier']),
      priority: (json['priority'] as num?)?.toInt() ?? 5,
      indexedAt: DateTime.parse(json['indexedAt'] as String),
      lastModified: json['lastModified'] == null
          ? null
          : DateTime.parse(json['lastModified'] as String),
      lastAccessed: json['lastAccessed'] == null
          ? null
          : DateTime.parse(json['lastAccessed'] as String),
      structuredData:
          json['structuredData'] as Map<String, dynamic>? ?? const {},
      metadata: json['metadata'] as Map<String, dynamic>? ?? const {},
      keywords: (json['keywords'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      tags:
          (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      snippet: json['snippet'] as String?,
      title: json['title'] as String? ?? '',
      summary: json['summary'] as String?,
      content: json['content'] as String?,
    );

Map<String, dynamic> _$$UniversalIndexEntryImplToJson(
        _$UniversalIndexEntryImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'connectorId': instance.connectorId,
      'contentType': _$UniversalContentTypeEnumMap[instance.contentType]!,
      'primaryKey': instance.primaryKey,
      'searchableText': instance.searchableText,
      'displayName': instance.displayName,
      'indexTier': _$IndexTierEnumMap[instance.indexTier]!,
      'priority': instance.priority,
      'indexedAt': instance.indexedAt.toIso8601String(),
      'lastModified': instance.lastModified?.toIso8601String(),
      'lastAccessed': instance.lastAccessed?.toIso8601String(),
      'structuredData': instance.structuredData,
      'metadata': instance.metadata,
      'keywords': instance.keywords,
      'tags': instance.tags,
      'score': instance.score,
      'snippet': instance.snippet,
      'title': instance.title,
      'summary': instance.summary,
      'content': instance.content,
    };

const _$UniversalContentTypeEnumMap = {
  UniversalContentType.filePath: 'file_path',
  UniversalContentType.url: 'url',
  UniversalContentType.email: 'email',
  UniversalContentType.phone: 'phone',
  UniversalContentType.text: 'text',
  UniversalContentType.contact: 'contact',
  UniversalContentType.document: 'document',
  UniversalContentType.image: 'image',
  UniversalContentType.audio: 'audio',
  UniversalContentType.video: 'video',
  UniversalContentType.code: 'code',
  UniversalContentType.other: 'other',
};

const _$IndexTierEnumMap = {
  IndexTier.hot: 'hot',
  IndexTier.warm: 'warm',
  IndexTier.cold: 'cold',
};

_$IndexSearchResultImpl _$$IndexSearchResultImplFromJson(
        Map<String, dynamic> json) =>
    _$IndexSearchResultImpl(
      query: json['query'] as String,
      results: (json['results'] as List<dynamic>)
          .map((e) => UniversalIndexEntry.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalCount: (json['totalCount'] as num).toInt(),
      searchTime: Duration(microseconds: (json['searchTime'] as num).toInt()),
      facets: (json['facets'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toInt()),
      ),
    );

Map<String, dynamic> _$$IndexSearchResultImplToJson(
        _$IndexSearchResultImpl instance) =>
    <String, dynamic>{
      'query': instance.query,
      'results': instance.results,
      'totalCount': instance.totalCount,
      'searchTime': instance.searchTime.inMicroseconds,
      'facets': instance.facets,
    };

_$UnifiedEntityMetadataImpl _$$UnifiedEntityMetadataImplFromJson(
        Map<String, dynamic> json) =>
    _$UnifiedEntityMetadataImpl(
      entityId: json['entityId'] as String,
      name: json['name'] as String,
      type: $enumDecode(_$UnifiedEntityTypeEnumMap, json['type']),
      description: json['description'] as String?,
      properties: json['properties'] as Map<String, dynamic>?,
      tags:
          (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ??
              const [],
      accessCount: (json['accessCount'] as num?)?.toInt() ?? 0,
      lastAccessed: json['lastAccessed'] == null
          ? null
          : DateTime.parse(json['lastAccessed'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      entityType: json['entityType'] as String?,
      displayName: json['displayName'] as String?,
      importance: (json['importance'] as num?)?.toDouble() ?? 0.0,
    );

Map<String, dynamic> _$$UnifiedEntityMetadataImplToJson(
        _$UnifiedEntityMetadataImpl instance) =>
    <String, dynamic>{
      'entityId': instance.entityId,
      'name': instance.name,
      'type': _$UnifiedEntityTypeEnumMap[instance.type]!,
      'description': instance.description,
      'properties': instance.properties,
      'tags': instance.tags,
      'accessCount': instance.accessCount,
      'lastAccessed': instance.lastAccessed?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
      'entityType': instance.entityType,
      'displayName': instance.displayName,
      'importance': instance.importance,
    };

const _$UnifiedEntityTypeEnumMap = {
  UnifiedEntityType.file: 'file',
  UnifiedEntityType.person: 'person',
  UnifiedEntityType.concept: 'concept',
  UnifiedEntityType.project: 'project',
  UnifiedEntityType.reference: 'reference',
  UnifiedEntityType.unknown: 'unknown',
};

_$UnifiedEntityRelationshipImpl _$$UnifiedEntityRelationshipImplFromJson(
        Map<String, dynamic> json) =>
    _$UnifiedEntityRelationshipImpl(
      sourceEntityId: json['sourceEntityId'] as String,
      targetEntityId: json['targetEntityId'] as String,
      relationshipType: json['relationshipType'] as String,
      strength: (json['strength'] as num?)?.toInt() ?? 1,
      description: json['description'] as String?,
      properties: json['properties'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$UnifiedEntityRelationshipImplToJson(
        _$UnifiedEntityRelationshipImpl instance) =>
    <String, dynamic>{
      'sourceEntityId': instance.sourceEntityId,
      'targetEntityId': instance.targetEntityId,
      'relationshipType': instance.relationshipType,
      'strength': instance.strength,
      'description': instance.description,
      'properties': instance.properties,
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };

_$GraphNodeImpl _$$GraphNodeImplFromJson(Map<String, dynamic> json) =>
    _$GraphNodeImpl(
      id: json['id'] as String,
      label: json['label'] as String,
      nodeType: json['nodeType'] as String?,
      attributes: json['attributes'] as Map<String, dynamic>?,
      weight: (json['weight'] as num?)?.toDouble() ?? 1.0,
      importance: (json['importance'] as num?)?.toDouble() ?? 1.0,
      centralityScore: (json['centralityScore'] as num?)?.toDouble() ?? 0.0,
    );

Map<String, dynamic> _$$GraphNodeImplToJson(_$GraphNodeImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'label': instance.label,
      'nodeType': instance.nodeType,
      'attributes': instance.attributes,
      'weight': instance.weight,
      'importance': instance.importance,
      'centralityScore': instance.centralityScore,
    };

_$GraphEdgeImpl _$$GraphEdgeImplFromJson(Map<String, dynamic> json) =>
    _$GraphEdgeImpl(
      source: json['source'] as String,
      target: json['target'] as String,
      edgeType: json['edgeType'] as String?,
      weight: (json['weight'] as num?)?.toDouble() ?? 1.0,
      attributes: json['attributes'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$GraphEdgeImplToJson(_$GraphEdgeImpl instance) =>
    <String, dynamic>{
      'source': instance.source,
      'target': instance.target,
      'edgeType': instance.edgeType,
      'weight': instance.weight,
      'attributes': instance.attributes,
    };

_$UnifiedGraphDataImpl _$$UnifiedGraphDataImplFromJson(
        Map<String, dynamic> json) =>
    _$UnifiedGraphDataImpl(
      nodes: (json['nodes'] as List<dynamic>)
          .map((e) => GraphNode.fromJson(e as Map<String, dynamic>))
          .toList(),
      edges: (json['edges'] as List<dynamic>)
          .map((e) => GraphEdge.fromJson(e as Map<String, dynamic>))
          .toList(),
      graphAttributes: json['graphAttributes'] as Map<String, dynamic>?,
      graphType: json['graphType'] as String?,
      isDirected: json['isDirected'] as bool? ?? false,
      lastUpdated: DateTime.parse(json['lastUpdated'] as String),
      clusters: (json['clusters'] as Map<String, dynamic>?)?.map(
        (k, e) =>
            MapEntry(k, (e as List<dynamic>).map((e) => e as String).toList()),
      ),
      centrality: (json['centrality'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
    );

Map<String, dynamic> _$$UnifiedGraphDataImplToJson(
        _$UnifiedGraphDataImpl instance) =>
    <String, dynamic>{
      'nodes': instance.nodes,
      'edges': instance.edges,
      'graphAttributes': instance.graphAttributes,
      'graphType': instance.graphType,
      'isDirected': instance.isDirected,
      'lastUpdated': instance.lastUpdated.toIso8601String(),
      'clusters': instance.clusters,
      'centrality': instance.centrality,
    };

_$UnifiedVectorDocumentImpl _$$UnifiedVectorDocumentImplFromJson(
        Map<String, dynamic> json) =>
    _$UnifiedVectorDocumentImpl(
      documentId: json['documentId'] as String,
      content: json['content'] as String,
      title: json['title'] as String?,
      contentType: json['contentType'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      embedding: (json['embedding'] as List<dynamic>)
          .map((e) => (e as num).toDouble())
          .toList(),
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      sourceConnector: json['sourceConnector'] as String?,
      sourcePath: json['sourcePath'] as String?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );

Map<String, dynamic> _$$UnifiedVectorDocumentImplToJson(
        _$UnifiedVectorDocumentImpl instance) =>
    <String, dynamic>{
      'documentId': instance.documentId,
      'content': instance.content,
      'title': instance.title,
      'contentType': instance.contentType,
      'metadata': instance.metadata,
      'embedding': instance.embedding,
      'score': instance.score,
      'sourceConnector': instance.sourceConnector,
      'sourcePath': instance.sourcePath,
      'timestamp': instance.timestamp.toIso8601String(),
    };

_$VectorSearchResultImpl _$$VectorSearchResultImplFromJson(
        Map<String, dynamic> json) =>
    _$VectorSearchResultImpl(
      query: json['query'] as String,
      queryEmbedding: (json['queryEmbedding'] as List<dynamic>)
          .map((e) => (e as num).toDouble())
          .toList(),
      results: (json['results'] as List<dynamic>)
          .map((e) => UnifiedVectorDocument.fromJson(e as Map<String, dynamic>))
          .toList(),
      totalCount: (json['totalCount'] as num).toInt(),
      searchTime: Duration(microseconds: (json['searchTime'] as num).toInt()),
      similarityMetric: json['similarityMetric'] as String? ?? 'cosine',
    );

Map<String, dynamic> _$$VectorSearchResultImplToJson(
        _$VectorSearchResultImpl instance) =>
    <String, dynamic>{
      'query': instance.query,
      'queryEmbedding': instance.queryEmbedding,
      'results': instance.results,
      'totalCount': instance.totalCount,
      'searchTime': instance.searchTime.inMicroseconds,
      'similarityMetric': instance.similarityMetric,
    };

_$VectorClusterImpl _$$VectorClusterImplFromJson(Map<String, dynamic> json) =>
    _$VectorClusterImpl(
      clusterId: json['clusterId'] as String,
      documentIds: (json['documentIds'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      centroid: (json['centroid'] as List<dynamic>)
          .map((e) => (e as num).toDouble())
          .toList(),
      cohesion: (json['cohesion'] as num?)?.toDouble() ?? 0.0,
      topic: json['topic'] as String?,
      keywords: (json['keywords'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$$VectorClusterImplToJson(_$VectorClusterImpl instance) =>
    <String, dynamic>{
      'clusterId': instance.clusterId,
      'documentIds': instance.documentIds,
      'centroid': instance.centroid,
      'cohesion': instance.cohesion,
      'topic': instance.topic,
      'keywords': instance.keywords,
    };

_$UnifiedApiResponseImpl _$$UnifiedApiResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$UnifiedApiResponseImpl(
      success: json['success'] as bool,
      data: json['data'] as Map<String, dynamic>?,
      error: json['error'] as String?,
      message: json['message'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );

Map<String, dynamic> _$$UnifiedApiResponseImplToJson(
        _$UnifiedApiResponseImpl instance) =>
    <String, dynamic>{
      'success': instance.success,
      'data': instance.data,
      'error': instance.error,
      'message': instance.message,
      'metadata': instance.metadata,
      'timestamp': instance.timestamp.toIso8601String(),
    };

_$DataSourceStatsImpl _$$DataSourceStatsImplFromJson(
        Map<String, dynamic> json) =>
    _$DataSourceStatsImpl(
      dataType: json['dataType'] as String,
      totalCount: (json['totalCount'] as num).toInt(),
      activeCount: (json['activeCount'] as num).toInt(),
      lastUpdated: DateTime.parse(json['lastUpdated'] as String),
      breakdown: (json['breakdown'] as Map<String, dynamic>?)?.map(
        (k, e) => MapEntry(k, (e as num).toInt()),
      ),
      metrics: json['metrics'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$$DataSourceStatsImplToJson(
        _$DataSourceStatsImpl instance) =>
    <String, dynamic>{
      'dataType': instance.dataType,
      'totalCount': instance.totalCount,
      'activeCount': instance.activeCount,
      'lastUpdated': instance.lastUpdated.toIso8601String(),
      'breakdown': instance.breakdown,
      'metrics': instance.metrics,
    };
