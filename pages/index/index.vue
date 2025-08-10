<template>
  <view class="container">
    <!-- 上传按钮 -->
    <button @click="chooseFile" type="primary" class="upload-btn">选择文件上传</button>
    
    <!-- 图片预览 -->
    <image v-if="imageUrl" :src="imageUrl" mode="aspectFit" class="preview-image"></image>
    
    <!-- 识别结果 -->
    <view class="result-box">
      <text class="title">图片识别结果：</text>
      <scroll-view scroll-y class="content-box">
        <text>{{ ocrResult || '等待识别...' }}</text>
      </scroll-view>
    </view>
    
    <!-- 业务分析结果 -->
    <view class="result-box">
      <text class="title">成绩分析结果：</text>
      <scroll-view scroll-y class="content-box analysis-box">
        <text>{{ analysisResult || '等待分析...' }}</text>
      </scroll-view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue';

// 响应式数据
const imageUrl = ref('');
const ocrResult = ref('');
const analysisResult = ref('');

// 选择文件
const chooseFile = async () => {
  try {
    // 选择文件
    const res = await uni.chooseImage({
      count: 1,
      sourceType: ['album', 'camera'],
      sizeType: ['compressed']
    });
    
    // 显示图片预览
    imageUrl.value = res.tempFilePaths[0];
    
    // 模拟OCR识别过程
    ocrResult.value = '正在识别图片内容...';
    setTimeout(() => {
      // 这里是模拟OCR识别结果
      ocrResult.value = `识别成功！\n\n科目\t成绩\n数学\t92\n语文\t88\n英语\t95\n物理\t85\n化学\t90`;
      
      // 自动触发分析
      analyzeResults();
    }, 1500);
  } catch (err) {
    uni.showToast({
      title: '选择文件失败',
      icon: 'none'
    });
  }
};

// 分析识别结果
const analyzeResults = () => {
  if (!ocrResult.value) return;
  
  // 模拟分析过程
  analysisResult.value = '正在分析成绩...';
  setTimeout(() => {
    // 从OCR结果中提取成绩数据（实际项目中需要更复杂的解析）
    const scores = [];
    const lines = ocrResult.value.split('\n');
    lines.forEach(line => {
      if (line.includes('\t')) {
        const [subject, score] = line.split('\t');
        if (!isNaN(score)) {
          scores.push({ subject, score: parseInt(score) });
        }
      }
    });
    
    // 计算分析结果
    if (scores.length > 0) {
      const total = scores.reduce((sum, item) => sum + item.score, 0);
      const average = total / scores.length;
      const bestSubject = scores.reduce((prev, current) => 
        (prev.score > current.score) ? prev : current
      );
      
      analysisResult.value = `分析完成：
平均分：${average.toFixed(1)}
总分：${total}
最佳科目：${bestSubject.subject}（${bestSubject.score}分）
${average > 90 ? '成绩优秀！' : average > 80 ? '成绩良好' : '需要继续努力'}`;
    } else {
      analysisResult.value = '未能识别到有效成绩数据';
    }
  }, 1000);
};
</script>

<style scoped>
.container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-btn {
  margin-bottom: 20px;
}

.preview-image {
  width: 100%;
  height: 300px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.result-box {
  border: 1px solid #eaeaea;
  border-radius: 8px;
  padding: 12px;
}

.title {
  font-weight: bold;
  margin-bottom: 8px;
  display: block;
}

.content-box {
  max-height: 200px;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.analysis-box {
  background-color: #f0f8ff;
}
</style>