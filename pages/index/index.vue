<template>
	<view class="container">
		<view class="header-banner">
			<text class="banner-title">开启您的孕期智能分析</text>
			<text class="banner-subtitle">上传B超图片，获取专业评估</text>
		</view>

		<view class="content-card">
			<view class="upload-section">
				<button @click="chooseImage" :loading="isLoading" :disabled="isLoading" class="upload-btn">
					<view class="button-content">
						<text class="upload-icon">+</text>
						<text>{{ isLoading ? '分析中...' : '上传图片' }}</text>
					</view>
				</button>
			</view>

			<view v-if="imageUrl" class="preview-section">
				<text class="section-title">图片预览</text>
				<image :src="imageUrl" mode="aspectFit" class="preview-image"></image>
			</view>

			<view v-if="analysisResult" class="result-section">
				<text class="section-title">分析报告</text>
				<view class="result-list">
					<view class="result-item">
						<text class="label">胎停育风险</text>
						<text class="value" :class="{'risk-high': analysisResult.risk === '高'}">{{ analysisResult.risk || '-' }}</text>
					</view>
					<view class="result-item">
						<text class="label">自然流产概率</text>
						<text class="value">{{ analysisResult.probability || '-' }}</text>
					</view>
					<view class="result-item">
						<text class="label">建议复查日期</text>
						<text class="value">{{ analysisResult.nextCheckupDate || '无' }}</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue';

// 定义后端API地址
const UPLOAD_URL = 'https://your-backend-api.com/analyze-bultrasound';

// 响应式数据
const imageUrl = ref('');
const analysisResult = ref(null);
const isLoading = ref(false);

/**
 * 封装的图片上传和分析函数
 * @param {string} filePath - 图片的临时文件路径
 */
const analyzeImage = async (filePath) => {
	try {
		const uploadResponse = await uni.uploadFile({
			url: UPLOAD_URL,
			filePath: filePath,
			name: 'imageFile',
			timeout: 60000,
		});

		const data = JSON.parse(uploadResponse.data);
		
		if (data.code !== 200) {
			throw new Error(data.message || '图片分析失败，请稍后重试。');
		}

		analysisResult.value = data.data;

	} catch (err) {
		console.error('分析失败:', err);
		uni.showToast({
			title: err.message || '图片上传或分析过程中出现错误',
			icon: 'none',
			duration: 3000
		});
		analysisResult.value = null;
	}
};

/**
 * 选择图片并触发分析流程
 */
const chooseImage = async () => {
	if (isLoading.value) return;
	
	try {
		const res = await uni.chooseImage({
			count: 1,
			sourceType: ['album', 'camera'],
			sizeType: ['compressed']
		});
		
		const tempFilePath = res.tempFilePaths?.[0];
		if (!tempFilePath) return;

		imageUrl.value = tempFilePath;
		analysisResult.value = null;

		isLoading.value = true;
		uni.showLoading({
			title: '正在智能分析...',
			mask: true
		});

		await analyzeImage(tempFilePath);

	} catch (err) {
		console.error('选择图片失败:', err);
		uni.showToast({
			title: '取消选择或发生错误',
			icon: 'none'
		});
	} finally {
		isLoading.value = false;
		uni.hideLoading();
	}
};
</script>

<style scoped>
/* 容器样式 - 柔和背景 */
.container {
	display: flex;
	flex-direction: column;
	align-items: center;
	min-height: 100vh;
	padding: 40rpx;
	box-sizing: border-box;
	background-color: #f7f9fc; /* 柔和的浅蓝色背景，替代纯白 */
}

/* 欢迎横幅 */
.header-banner {
	width: 100%;
	text-align: center;
	margin-bottom: 60rpx; /* 增加间距 */
}

/* 标题和副标题都设置为块级元素，使其独占一行 */
.banner-title, .banner-subtitle {
	display: block; 
}

.banner-title {
	font-size: 40rpx; /* 字体增大 */
	font-weight: bold;
	color: #333;
	margin-bottom: 8rpx;
}

.banner-subtitle {
	font-size: 28rpx;
	color: #777;
}

/* 主体内容卡片 */
.content-card {
	width: 100%;
	max-width: 650rpx;
	background-color: #fff;
	border-radius: 24rpx;
	padding: 50rpx 40rpx; /* 增加内边距 */
	box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.08);
	display: flex;
	flex-direction: column;
	gap: 50rpx; /* 增加模块间距 */
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
	background: linear-gradient(45deg, #66e0c6, #37a898); /* 渐变色按钮，更具活力 */
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
</style>