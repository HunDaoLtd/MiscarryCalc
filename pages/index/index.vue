<template>
	<view class="container">
		<!-- <view class="header-banner">
			<text class="banner-title">孕周智能分析</text>
			<text class="banner-subtitle">上传B超图片，获取专业评估</text>
		</view> -->

		<view class="content-card">
			<view class="upload-section">
				<button @click="chooseImage" :loading="isLoading" :disabled="isLoading" class="upload-btn">
					<view class="button-content">
						<text class="upload-icon">+</text>
						<text>{{ isLoading ? '分析中...' : '拍摄超声报告单' }}</text>
					</view>
				</button>
				<!-- 新增测试按钮 -->
				<button @click="testAnalysis" class="upload-btn" style="margin-left:20rpx;background:linear-gradient(45deg,#ffd966,#f6b26b);">
					<view class="button-content">
						<text class="upload-icon">🧪</text>
						<text>测试</text>
					</view>
				</button>
			</view>
			<view v-if="uploadStatus" class="status-message">{{ uploadStatus }}</view>

			<view v-if="imageUrl" class="preview-section">
				<text class="section-title">图片预览</text>
				<image :src="imageUrl" mode="aspectFit" class="preview-image"></image>
			</view>

			<view v-if="analysisResult" class="result-section">
				<text class="section-title">分析报告</text>
				<view class="result-list">
					<view class="result-item">
						<text class="label">孕囊大小 (GS)</text>
						<text class="value">{{ analysisResult['孕囊大小'] ?? '-' }} mm</text>
					</view>
					<view class="result-item">
						<text class="label">胚芽长 (CRL)</text>
						<text class="value">{{ analysisResult['胚芽长'] ?? '-' }} mm</text>
					</view>
					<view class="result-item">
						<text class="label">是否停育</text>
						<text class="value">{{ analysisResult['是否停育'] ? '是' : '否' }}</text>
					</view>
					<view class="result-item">
						<text class="label">超声检查日期</text>
						<text class="value">{{ analysisResult['日期'] ?? '-' }}</text>
					</view>
				</view>
				<view class="section-title" style="margin-top:30rpx;">孕周估算</view>
				<view class="result-list">
					<view v-if="!analysisResult['胚芽长']" class="result-item">
						<text class="label">孕囊估算</text>
						<text class="value">{{ analysisResult.GA0 }} 周</text>
					</view>
					<view v-else>
						<view class="result-item">
							<text class="label">Robinson公式 (推荐)</text>
							<text class="value">🌟 {{ analysisResult.GA1 }} 周</text>
						</view>
						<view class="result-item">
							<text class="label">回归方程</text>
							<text class="value">{{ analysisResult.GA2 }} 周</text>
						</view>
						<view class="result-item">
							<text class="label">经验法则</text>
							<text class="value">{{ analysisResult.GA3 }} 周</text>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue';

// 响应式数据
const imageUrl = ref('');
const analysisResult = ref('');
const uploadStatus = ref('');

// 选择文件
async function chooseImage() {
  try {
    uploadStatus.value = '选择文件中...';
    
    const res = await uni.chooseImage({
      count: 1,
      sourceType: ['album', 'camera'],
      sizeType: ['compressed']
    });
    
    const filePath = res.tempFilePaths[0];
    imageUrl.value = filePath;

    // 获取文件扩展名和内容类型
    const ext = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();
    let contentType = 'application/octet-stream';
    if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';
    else if (ext === '.png') contentType = 'image/png';
    else if (ext === '.gif') contentType = 'image/gif';
    else if (ext === '.bmp') contentType = 'image/bmp';
    else if (ext === '.webp') contentType = 'image/webp';
    else if (ext === '.avif') contentType = 'image/avif';

    // 将contentType传递给uploadFile
    await uploadFile(filePath, contentType, ext);
  } catch (err) {
    console.error('选择文件失败:', err);
    uploadStatus.value = '选择文件失败';
    uni.showToast({
      title: '选择文件失败',
      icon: 'none'
    });
  }
};

// 文件上传函数
async function uploadFile(filePath, contentType, ext) {
  if (!ext) ext = '.jpg'; // 设置默认扩展名
  try {
    uploadStatus.value = '上传中...';
    analysisResult.value = '';

    const fileName = `score_${Date.now()}${ext}`;
    const apiUrl = `https://apps.hundao.xyz/rendered/${fileName}`;
    
    // 使用uni.uploadFile API
    await new Promise((resolve, reject) => {
      const task = uni.uploadFile({
        url: apiUrl,
        filePath: filePath,
        name: 'file',
        fileType: 'image',
        formData: {
          'filename': fileName
        },
        header: {
          'Content-Type': contentType,
        },
        success: (uploadRes) => {
          if (uploadRes.statusCode === 200) {
            // 上传成功，开始获取分析结果
            getAnalysisResult(fileName).then(resolve).catch(reject);
          } else {
            reject(new Error(`上传失败，状态码: ${uploadRes.statusCode}`));
          }
        },
        fail: (err) => {
          reject(new Error(`上传失败: ${err.errMsg}`));
        }
      });
      
      // 监听上传进度
      task.onProgressUpdate(function(res) {
        uploadStatus.value = `上传中 ${res.progress}%`;
      });
    });
    
  } catch (err) {
    console.error('上传失败:', err);
    uploadStatus.value = '上传失败: ' + err.message;
    uni.showToast({
      title: '上传失败',
      icon: 'none'
    });
  }
};

// 获取分析结果的函数
async function getAnalysisResult(fileName) {
  try {
    uploadStatus.value = '分析中...';
    
    // 这里假设后端分析完成后可以通过这个URL获取结果
    const analysisUrl = `https://apps.hundao.xyz/1_MiscarryCalc/analysis/${fileName}`;
    
    // 发送请求获取分析结果
    const res = await uni.request({
      url: analysisUrl,
      method: 'GET',
      timeout: 60000 // 60秒超时
    });
    // console.log('获取分析结果:', res.data);

    if (res.statusCode === 200 && res.data) {
      calculateAnalysisResults(res.data);
      uploadStatus.value = '分析完成';
      return true;
    } else {
      throw new Error(`分析失败，状态码: ${res.statusCode}`);
    }
  } catch (err) {
    console.error('获取分析结果失败:', err);
    uploadStatus.value = '分析失败: ' + err.message;
    uni.showToast({
      title: '分析失败',
      icon: 'none'
    });
    throw err;
  }
};

// 分析结果计算
async function calculateAnalysisResults(result) {
  analysisResult.value = result;
  // 计算孕周
  const GS = result["孕囊大小"];
  const CRL = result["胚芽长"];
  let GA0, GA1, GA2, GA3;
  if (GS !== undefined && GS !== null) GA0 = (GS + 30) / 7;       // 0. 孕囊估算（适用于5-6周前的早期评估）
  if (CRL !== undefined && CRL !== null) {
    GA1 = (8.052 * Math.pow(CRL * 1.037, 0.5) + 23.73) / 7;       // 1. Robinson公式（国际公认标准方法）
    GA2 = 5.2876 + (0.1584 * CRL) - (0.0007 * Math.pow(CRL, 2));  // 2. 回归方程（其他研究提出）
    GA3 = CRL / 10 + 6.5;                                         // 3. 经验法则（简易快速估算）                  
  }
  analysisResult.value.GA0 = GA0 ? GA0.toFixed(2) : '-';
  analysisResult.value.GA1 = GA1 ? GA1.toFixed(2) : '-';
  analysisResult.value.GA2 = GA2 ? GA2.toFixed(2) : '-';
  analysisResult.value.GA3 = GA3 ? GA3.toFixed(2) : '-';
}

// 新增测试方法
async function testAnalysis() {
  try {
    uploadStatus.value = '测试中...';
    const res = await uni.request({
      url: 'https://apps.hundao.xyz/1_MiscarryCalc/analysis/test',
      method: 'GET',
      timeout: 30000
    });
    if (res.statusCode === 200) {
      calculateAnalysisResults(res.data);
      uploadStatus.value = '测试完成';
    } else {
      uploadStatus.value = '测试失败';
      uni.showToast({ title: '测试失败', icon: 'none' });
    }
  } catch (err) {
    uploadStatus.value = '测试异常';
    uni.showToast({ title: '测试异常', icon: 'none' });
  }
}

// [临床说明]
// 1. Robinson公式是国际妇产科联盟(FIGO)推荐的首选方法
// 2. 孕周估算误差范围通常为±5天（95%置信区间）
// 3. 实际孕周需结合末次月经日期综合判断

</script>

<style scoped>
/* 容器样式 - 柔和背景 */
.container {
	display: flex;
	flex-direction: column;
	align-items: center;
	min-height: 100%;
	box-sizing: border-box;
	background-color: #f7f9fc; /* 柔和的浅蓝色背景，替代纯白 */
}

/* 欢迎横幅 */
/* .header-banner {
	width: 100%;
	text-align: center;
	margin-bottom: 50rpx;
} */

/* 标题和副标题都设置为块级元素，使其独占一行 */
/* .banner-title, .banner-subtitle {
	display: block; 
}

.banner-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 8rpx;
}

.banner-subtitle {
	font-size: 28rpx;
	color: #777;
} */

/* 主体内容卡片 */
.content-card {
	width: 100%;
	max-width: 650rpx;
	background-color: #fff;
	border-radius: 24rpx;
	padding: 40rpx 30rpx; /* 内边距 */
	box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.08);
	display: flex;
	flex-direction: column;
	gap: 30rpx; /* 模块间距 */
}

/* 区域标题 */
.section-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx; /* 标题与内容间距 */
}

/* 上传区域 */
.upload-section {
	display: flex;
	justify-content: center;
}

/* 上传按钮 - 更有活力的渐变色 */
.upload-btn {
	width: 100%;
	background: linear-gradient(45deg, #66e0c6, #37a898); /* 渊变色按钮，更具活力 */
	color: #fff;
	font-size: 32rpx;
	padding: 24rpx;
	border-radius: 16rpx;
	box-shadow: 0 8rpx 20rpx rgba(55, 168, 152, 0.3);
	transition: all 0.2s ease-in-out;
	border: none;
}
.upload-btn::after { border: none; }

.upload-btn[disabled] {
	opacity: 0.6;
	background: #ccc;
	box-shadow: none;
}

.button-content {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 16rpx;
}

.upload-icon {
	font-size: 44rpx;
	line-height: 1;
	font-weight: bold;
}

/* 图片预览区域 */
.preview-section {
	display: flex;
	flex-direction: column;
}

.preview-image {
	width: 100%;
	height: 360rpx;
	border-radius: 12rpx;
	background-color: #f0f0f0; /* 图片加载前的背景色 */
	margin-top: 10rpx;
}

/* 结果区域 */
.result-section {
	display: flex;
	flex-direction: column;
}

.result-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.result-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 32rpx;
	background-color: #f7f9fc; /* 结果项的背景色，与主背景呼应 */
	border-radius: 12rpx;
	padding: 24rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.label {
	color: #666;
	flex: 1;
}

.value {
	font-weight: bold;
	text-align: right;
	flex: 1;
	color: #333;
}

.risk-high {
	color: #e74c3c;
}

.status-message {
  color: #007AFF;
  font-size: 14px;
  text-align: center;
  margin-bottom: 10px;
}
</style>