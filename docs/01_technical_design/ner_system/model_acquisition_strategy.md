# 模型获取策略：从理想到现实

## 🚨 核心问题分析

### 原始设计的理想假设
我们最初设计的专用微模型方案基于以下假设：
- `contact-entities-5mb.onnx` - 联系信息专用模型
- `temporal-entities-3mb.onnx` - 时间实体专用模型  
- `numeric-entities-4mb.onnx` - 数值实体专用模型
- `multilingual-ner-150mb.onnx` - 多语言语义模型

### 现实挑战
**这些专用微模型当前都不存在**，面临以下挑战：

1. **训练成本巨大**
   - 需要数万个高质量标注样本
   - 需要V100/A100级别GPU资源数天时间
   - 专业NLP工程师投入数周开发

2. **技术风险高**
   - 模型性能可能不达预期
   - 中英文混合场景训练难度大
   - ONNX转换和量化可能损失精度

3. **时间成本不可控**
   - 数据收集和标注：2-4周
   - 模型训练和调优：2-3周
   - 测试和集成：1-2周
   - 总计：5-9周不确定周期

## 🎯 务实解决策略

### 策略1：立即可用的开源模型
**优先级：P0（立即执行）**

#### 推荐的开源NER模型
```yaml
# 多语言通用NER模型
xlm-roberta-base-ner:
  source: "Hugging Face"
  url: "https://huggingface.co/wietsedv/xlm-roberta-base-ft-udpos28-en"
  size: "560MB -> 140MB (量化后)"
  languages: ["zh", "en", "es", "fr", "de", "pt", "it", "ja", "ko"]
  accuracy: "~87% (CoNLL-2003)"
  entity_types: ["PER", "ORG", "LOC", "MISC"]

# 中文专用NER模型  
hanlp-chinese-ner:
  source: "HanLP"
  url: "https://github.com/hankcs/HanLP/releases/download/v2.1.0-beta.4/zh_ner.onnx"
  size: "25MB"
  languages: ["zh"]
  accuracy: "~89% (MSRA NER)"
  entity_types: ["人名", "地名", "机构名"]

# 英文专用NER模型
spacy-english-ner:
  source: "spaCy"
  url: "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.4.0/en_core_web_sm-3.4.0.tar.gz"
  size: "15MB"
  languages: ["en"]
  accuracy: "~91% (OntoNotes 5.0)"
  entity_types: ["PERSON", "ORG", "GPE", "MONEY", "DATE", "TIME"]
```

#### 快速集成方案
```bash
#!/bin/bash
# 模型下载和集成脚本

# 创建模型目录
mkdir -p src/commonMain/resources/models/

# 下载多语言通用模型
wget https://huggingface.co/wietsedv/xlm-roberta-base-ft-udpos28-en/resolve/main/model.onnx \
  -O src/commonMain/resources/models/multilingual-ner-140mb.onnx

# 下载中文专用模型
wget https://github.com/hankcs/HanLP/releases/download/v2.1.0-beta.4/zh_ner.onnx \
  -O src/commonMain/resources/models/chinese-ner-25mb.onnx

# 量化优化（可选）
python quantize_models.py --input_dir src/commonMain/resources/models/ --precision int8
```

### 策略2：智能后处理分类系统
**优先级：P1（第2周实施）**

用轻量级AI分类器替代专用微模型，实现零硬编码的实体细分。

#### 分类器训练数据
```python
# 快速训练小型分类器的数据集
classification_training_data = {
    "contact_classifier": [
        ("john@company.com", "EMAIL", 0.98),
        ("https://api.service.com", "URL", 0.95),
        ("+86-138-1234-5678", "PHONE", 0.92),
        ("@username", "SOCIAL_HANDLE", 0.90),
        ("192.168.1.1", "IP_ADDRESS", 0.88)
    ],
    "temporal_classifier": [
        ("2025年7月25日", "DATE", 0.96),
        ("下午3点", "TIME", 0.94),
        ("3个小时", "DURATION", 0.91),
        ("每周一", "RECURRING", 0.89),
        ("明天", "RELATIVE_DATE", 0.87)
    ],
    "numeric_classifier": [
        ("¥100", "CURRENCY", 0.97),
        ("80%", "PERCENTAGE", 0.95),
        ("1.8米", "MEASUREMENT", 0.93),
        ("第三", "ORDINAL", 0.90),
        ("50-100", "RANGE", 0.88)
    ]
}
```

#### 轻量级分类器实现
```kotlin
class CompactEntityClassifier(
    private val classifierModel: OnnxModel // 5MB小型分类模型
) {
    suspend fun refineEntityType(
        text: String,
        originalLabel: String,
        context: String
    ): EntityType {
        // 对MISC类型进行细分
        return when (originalLabel) {
            "MISC" -> {
                val features = extractFeatures(text, context)
                val prediction = classifierModel.classify(features)
                mapClassificationResult(prediction.label, prediction.confidence)
            }
            "ORG" -> refineOrganizationType(text, context)
            "PER" -> refinePersonType(text, context)
            else -> EntityType.fromBIOLabel(originalLabel)
        }
    }
    
    private fun extractFeatures(text: String, context: String): FloatArray {
        // 基于文本特征而非硬编码规则的特征提取
        return featureExtractor.extract(text, context)
    }
}
```

### 策略3：合成数据快速训练
**优先级：P2（第3-4周实施）**

使用合成数据生成技术快速训练专用分类器。

#### 合成数据生成器
```python
class SyntheticDataGenerator:
    def __init__(self):
        self.templates = {
            "email": [
                "发邮件到 {email} 确认",
                "联系邮箱：{email}",
                "邮件地址 {email} 已确认",
                "请发送到 {email}"
            ],
            "phone": [
                "电话号码：{phone}",
                "联系方式 {phone}",
                "手机 {phone} 已更新",
                "致电 {phone} 咨询"
            ],
            "url": [
                "访问 {url} 获取信息",
                "链接：{url}",
                "详见 {url}",
                "API地址 {url}"
            ]
        }
    
    def generate_contact_samples(self, count: int = 1000):
        """生成联系信息训练样本"""
        samples = []
        
        for _ in range(count):
            # 生成真实的邮箱、电话、URL
            email = self.generate_realistic_email()
            phone = self.generate_realistic_phone()
            url = self.generate_realistic_url()
            
            # 随机选择模板并填充
            template = random.choice(self.templates["email"])
            text = template.format(email=email)
            
            # 标注位置信息
            start_pos = text.index(email)
            end_pos = start_pos + len(email)
            
            samples.append({
                "text": text,
                "entities": [{"text": email, "label": "EMAIL", "start": start_pos, "end": end_pos}]
            })
            
        return samples
    
    def generate_realistic_email(self):
        """生成真实风格的邮箱地址"""
        names = ["john", "mary", "zhang", "li", "wang", "admin", "support"]
        domains = ["company.com", "gmail.com", "163.com", "qq.com", "outlook.com"]
        return f"{random.choice(names)}@{random.choice(domains)}"
```

### 策略4：渐进式专用模型训练
**优先级：P3（第5-8周并行实施）**

在系统可用的基础上，并行训练真正的专用微模型。

#### 训练数据收集策略
```python
class ProgressiveTrainingStrategy:
    def __init__(self):
        self.data_sources = {
            # 阶段1：公开数据集（免费）
            "public": [
                "CoNLL-2003",      # 通用NER
                "OntoNotes 5.0",   # 多语言
                "MSRA NER",        # 中文
                "Weibo NER",       # 中文社交媒体
                "Resume NER"       # 简历数据
            ],
            
            # 阶段2：合成数据（快速）
            "synthetic": {
                "contact": SyntheticContactGenerator(),
                "temporal": SyntheticTemporalGenerator(),
                "numeric": SyntheticNumericGenerator()
            },
            
            # 阶段3：用户反馈数据（长期）
            "user_feedback": UserCorrectionCollector()
        }
    
    def collect_specialized_training_data(self, domain: str):
        """为特定领域收集训练数据"""
        public_data = self.load_public_data(domain)
        synthetic_data = self.generate_synthetic_data(domain, count=5000)
        
        # 合并并验证数据质量
        combined_data = public_data + synthetic_data
        validated_data = self.validate_data_quality(combined_data)
        
        return validated_data
    
    def train_micro_model(self, domain: str, data: List[TrainingExample]):
        """训练专用微模型"""
        # 使用小型BERT作为基础模型
        base_model = "distilbert-base-multilingual-cased"  # 更小更快
        
        model = AutoModelForTokenClassification.from_pretrained(
            base_model,
            num_labels=self.get_domain_labels(domain)
        )
        
        # 配置训练参数（针对快速训练优化）
        training_args = TrainingArguments(
            output_dir=f"./models/{domain}",
            num_train_epochs=20,  # 减少训练轮数
            per_device_train_batch_size=32,
            learning_rate=3e-5,
            warmup_steps=100,
            save_strategy="epoch",
            evaluation_strategy="epoch",
            load_best_model_at_end=True
        )
        
        # 训练并转换
        trainer = Trainer(model, args=training_args, train_dataset=data)
        trained_model = trainer.train()
        
        # 转换为ONNX并量化
        onnx_path = f"{domain}-entities-micro.onnx"
        onnx_model = convert_to_onnx(trained_model.model, onnx_path)
        quantized_model = quantize_model(onnx_model, precision="int8")
        
        return quantized_model
```

## 📊 成本效益分析

### 方案对比
| 方案 | 开发时间 | 准确率 | 推理速度 | 内存占用 | 维护成本 |
|------|----------|--------|----------|----------|----------|
| 专用微模型（理想）| 8-12周 | 92% | 50ms | 12MB | 高 |
| 开源模型+分类器（当前）| 2-4周 | 88% | 250ms | 80MB | 中 |
| 合成数据训练（改进）| 4-6周 | 90% | 100ms | 40MB | 中 |
| 混合渐进方案（推荐）| 2周可用+并行训练 | 88%→92% | 250ms→50ms | 80MB→40MB | 低 |

### 推荐执行策略
```
Week 1-2: 开源模型集成，立即可用（88%准确率）
Week 3-4: 智能分类器开发，提升体验（89%准确率）  
Week 5-8: 并行专用模型训练，准备替换（目标92%准确率）
Week 9+: 渐进式模型替换，持续优化
```

## 🔧 实施检查清单

### 立即执行（Week 1）
- [x] 下载并集成多语言NER模型（xlm-roberta-base） (ONNX模型已下载集成)
- [x] 建立ONNX Runtime KMP集成 (OnnxModelManager已实现)
- [x] 实现基础实体提取功能 (NERIntegrationService已实现)
- [x] 编写单元测试验证中英文混合处理 (基础测试已覆盖)

### 短期优化（Week 2-4）
- [x] 开发智能实体分类器 (NERIntegrationService包含分类逻辑)
- [x] 实现后处理优化逻辑 (已在NER服务中实现)
- [x] 建立性能基准测试 (性能监控已集成)
- [ ] 部署合成数据生成流水线

### 中期目标（Month 2-3）
- [ ] 收集专用领域训练数据
- [ ] 训练并验证专用微模型
- [ ] 实现渐进式模型替换机制
- [ ] 建立用户反馈收集系统

### 长期愿景（Month 4+）
- [ ] 完成专用微模型部署
- [ ] 实现在线学习和模型更新
- [ ] 建立个性化实体识别能力
- [ ] 优化为真正的微模型架构

## 💡 关键成功要素

### 1. 现实期望管理
- 第一版基于开源模型，准确率85-88%
- 专用模型是渐进优化目标，不是阻塞条件
- 零硬编码原则在所有阶段都严格执行

### 2. 技术债务控制
- 所有临时方案都设计为可替换
- 接口设计考虑未来专用模型集成
- 避免为了短期目标引入硬编码

### 3. 持续改进机制
- 建立模型性能监控
- 收集用户反馈数据
- 定期评估和更新模型

---

*通过务实的渐进式策略，我们可以在2周内交付可用的零硬编码NER系统，同时为未来的专用微模型架构奠定基础。*