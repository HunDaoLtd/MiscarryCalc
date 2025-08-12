<template>
	<view class="container">
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
						<text>非停测试</text>
					</view>
				</button>
        <button @click="testAnalysis2" class="upload-btn" style="margin-left:20rpx;background:linear-gradient(45deg,#ffd966,#f6b26b);">
					<view class="button-content">
						<text class="upload-icon">🧪</text>
						<text>停育测试</text>
					</view>
				</button>
			</view>
			<view v-if="uploadStatus" class="status-message">{{ uploadStatus }}</view>

			<!-- 并列显示两个分析报告 -->
			<view v-if="analysisResult && analysisResult['是否停育'] && prevAnalysisResult" class="comparison-section">
				<!-- 报告标题行 -->
				<view class="comparison-header">
					<text class="section-title">对比分析</text>
				</view>
				
				<!-- 图片预览区域 -->
				<view class="comparison-images">
					<view class="image-column">
						<text class="column-title">停育前报告</text>
						<view v-if="prevImageUrl" class="preview-section">
							<image :src="prevImageUrl" mode="aspectFit" class="preview-image"></image>
						</view>
					</view>
					<view class="image-column">
						<text class="column-title">当前报告</text>
						<view v-if="imageUrl" class="preview-section">
							<image :src="imageUrl" mode="aspectFit" class="preview-image"></image>
						</view>
					</view>
				</view>

				<!-- 基本信息对比 -->
				<view class="comparison-data">
					<text class="section-subtitle">基本信息</text>
					<view class="comparison-row">
						<text class="row-label">孕囊大小 (GS)</text>
						<text class="row-value">{{ prevAnalysisResult['孕囊大小'] ?? '-' }} mm</text>
						<text class="row-value">{{ analysisResult['孕囊大小'] ?? '-' }} mm</text>
					</view>
					<view class="comparison-row">
						<text class="row-label">胚芽长 (CRL)</text>
						<text class="row-value">{{ prevAnalysisResult['胚芽长'] ?? '-' }} mm</text>
						<text class="row-value">{{ analysisResult['胚芽长'] ?? '-' }} mm</text>
					</view>
					<view class="comparison-row">
						<text class="row-label">是否停育</text>
						<text class="row-value">{{ prevAnalysisResult['是否停育'] ? '是' : '否' }}</text>
						<text class="row-value">{{ analysisResult['是否停育'] ? '是' : '否' }}</text>
					</view>
					<view class="comparison-row">
						<text class="row-label">超声检查日期</text>
						<text class="row-value">{{ formatDate(prevAnalysisResult['日期']) }}</text>
						<text class="row-value">{{ formatDate(analysisResult['日期']) }}</text>
					</view>
				</view>

				<!-- 孕周估算对比 -->
				<view class="comparison-data">
					<text class="section-subtitle">孕周估算</text>
					<view v-if="!analysisResult['胚芽长'] || !prevAnalysisResult['胚芽长']" class="comparison-row">
						<text class="row-label">孕囊估算</text>
						<text class="row-value">{{ prevAnalysisResult.GA0 ?? '-' }} 周</text>
						<text class="row-value">{{ analysisResult.GA0 ?? '-' }} 周</text>
					</view>
					<view v-if="analysisResult['胚芽长'] && prevAnalysisResult['胚芽长']">
						<view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
							<text class="row-label">Robinson公式 (推荐)</text>
							<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA1) : (prevAnalysisResult.GA1 + ' 周') }}</text>
							<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA1) : (analysisResult.GA1 + ' 周') }}</text>
						</view>
						<view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
							<text class="row-label">回归方程</text>
							<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA2) : (prevAnalysisResult.GA2 + ' 周') }}</text>
							<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA2) : (analysisResult.GA2 + ' 周') }}</text>
						</view>
						<view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
							<text class="row-label">经验法则</text>
							<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA3) : (prevAnalysisResult.GA3 + ' 周') }}</text>
							<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA3) : (analysisResult.GA3 + ' 周') }}</text>
						</view>
					</view>
				</view>

        <!-- 停育分析 -->
         <view class="comparison-data">
					<text class="section-subtitle">停育分析</text>
					<view class="result-list">
						<view class="result-item">
							<text class="row-label">受孕日期</text>
							<text class="row-value">{{ calculateConceptionDate(prevAnalysisResult['日期'], prevAnalysisResult.GA1) }}</text>
						</view>
						<view class="result-item">
							<text class="row-label">停育日期</text>
							<text class="row-value">{{ calculateMiscarryDate(calculateConceptionDate(prevAnalysisResult['日期'], prevAnalysisResult.GA1), analysisResult.GA1) }}</text>
						</view>
						<view class="result-item">
							<text class="row-label">预自然流产日</text>
							<text class="row-value">{{ calculateNaturalMiscarryDate(calculateMiscarryDate(calculateConceptionDate(prevAnalysisResult['日期'], prevAnalysisResult.GA1), analysisResult.GA1)) }}</text>
						</view>
					</view>
         </view>
			</view>

			<!-- 原有分析报告显示（未停育或未上传前报告时） -->
			<view v-else-if="analysisResult" class="result-section">
        <view v-if="imageUrl && !prevImageUrl" class="preview-section">
          <text class="section-title">图片预览</text>
          <image :src="imageUrl" mode="aspectFit" class="preview-image"></image>
        </view>

				<text class="section-title">分析报告</text>
				
				<!-- 基本信息 -->
				<view class="single-report-data">
					<text class="section-subtitle">基本信息</text>
					<view class="result-list">
						<view class="result-item">
							<text class="row-label">孕囊大小 (GS)</text>
							<text class="row-value">{{ analysisResult['孕囊大小'] ?? '-' }} mm</text>
						</view>
						<view class="result-item">
							<text class="row-label">胚芽长 (CRL)</text>
							<text class="row-value">{{ analysisResult['胚芽长'] ?? '-' }} mm</text>
						</view>
						<view class="result-item">
							<text class="row-label">是否停育</text>
							<text class="row-value">{{ analysisResult['是否停育'] ? '是' : '否' }}</text>
						</view>
						<view class="result-item">
							<text class="row-label">超声检查日期</text>
							<text class="row-value">{{ formatDate(analysisResult['日期']) }}</text>
						</view>
					</view>
				</view>

				<!-- 孕周估算 -->
				<view class="single-report-data">
					<text class="section-subtitle">孕周估算</text>
					<view class="result-list">
						<view v-if="!analysisResult['胚芽长']" class="result-item">
							<text class="row-label">孕囊估算</text>
							<text class="row-value">{{ analysisResult.GA0 }} 周</text>
						</view>
						<view v-else>
							<view class="result-item clickable-row" @click="toggleRobinsonFormat">
								<text class="row-label">Robinson公式 (推荐)</text>
								<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA1) : (analysisResult.GA1 + ' 周') }}</text>
							</view>
							<view class="result-item clickable-row" @click="toggleRobinsonFormat">
								<text class="row-label">回归方程</text>
								<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA2) : (analysisResult.GA2 + ' 周') }}</text>
							</view>
							<view class="result-item clickable-row" @click="toggleRobinsonFormat">
								<text class="row-label">经验法则</text>
								<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA3) : (analysisResult.GA3 + ' 周') }}</text>
							</view>
						</view>
					</view>
				</view>

        <!-- 如果停育，显示上传胎停育前报告单按钮 -->
        <view v-if="analysisResult && analysisResult['是否停育']">
          <view class="single-report-data">
						<text class="section-subtitle">停育分析</text>
						<view class="result-list">
							<view class="result-item">
								<text class="row-label">受孕日期</text>
								<text class="row-value">需上传停育前报告</text>
							</view>
							<view class="result-item">
								<text class="row-label">停育日期</text>
								<text class="row-value">需上传停育前报告</text>
							</view>
							<view class="result-item">
								<text class="row-label">预自然流产日</text>
								<text class="row-value">需上传停育前报告</text>
							</view>
						</view>
						<view style="display:flex;flex-direction:column;gap:12rpx;margin-top:20rpx;">
							<button @click="choosePrevImage" class="upload-btn" style="background:linear-gradient(45deg,#b6b9ff,#e3d9fa);">
								<view class="button-content">
									<text class="upload-icon">+</text>
									<text>上传胎停育前报告单</text>
								</view>
							</button>
							<button @click="testAnalysis3" class="upload-btn" style="background:linear-gradient(45deg,#ffd966,#f6b26b);">
								<view class="button-content">
									<text class="upload-icon">+</text>
									<text>胎停育前测试</text>
								</view>
							</button>
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

// 用于存储胎停育前的图片和分析结果
const prevImageUrl = ref('');
const prevAnalysisResult = ref('');

// 控制Robinson公式显示格式（true: 周+天格式, false: 周格式）
const showWeeksAndDays = ref(false);

// 工具函数：统一的Toast显示
function showToast(title, icon = 'none') {
  uni.showToast({ title, icon });
}

// 工具函数：统一的状态管理
function updateStatus(message) {
  uploadStatus.value = message;
}

// 工具函数：统一的错误处理
function handleError(error, defaultMessage, statusMessage) {
  console.error(defaultMessage, error);
  updateStatus(statusMessage || (defaultMessage + ': ' + error.message));
  showToast(statusMessage || defaultMessage);
}

// 工具函数：获取文件扩展名和内容类型
function getFileTypeInfo(filePath) {
  const ext = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();
  let contentType = 'application/octet-stream';
  
  const typeMap = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.webp': 'image/webp',
    '.avif': 'image/avif'
  };
  
  contentType = typeMap[ext] || contentType;
  return { ext, contentType };
}

// 统一的图片选择函数
async function chooseImageUnified(isForPrevious = false) {
  try {
    updateStatus('选择文件中...');
    
    const res = await uni.chooseImage({
      count: 1,
      sourceType: ['album', 'camera'],
      sizeType: ['compressed']
    });
    
    const filePath = res.tempFilePaths[0];
    
    // 根据类型设置对应的图片URL
    if (isForPrevious) {
      prevImageUrl.value = filePath;
    } else {
      imageUrl.value = filePath;
    }

    const { ext, contentType } = getFileTypeInfo(filePath);
    await uploadFileUnified(filePath, contentType, ext, isForPrevious);
  } catch (err) {
    handleError(err, '选择文件失败', '选择文件失败');
  }
}

// 选择主报告单
async function chooseImage() {
  await chooseImageUnified(false);
}

// 选择胎停育前报告单
async function choosePrevImage() {
  await chooseImageUnified(true);
}

// 统一的文件上传函数
async function uploadFileUnified(filePath, contentType, ext, isForPrevious = false) {
  if (!ext) ext = '.jpg';
  try {
    updateStatus('上传中...');
    
    // 根据类型清空对应的结果
    if (isForPrevious) {
      prevAnalysisResult.value = '';
    } else {
      analysisResult.value = '';
    }

    const prefix = isForPrevious ? 'prev_' : 'score_';
    const fileName = `${prefix}${Date.now()}${ext}`;
    const apiUrl = `https://apps.hundao.xyz/rendered/${fileName}`;
    
    await new Promise((resolve, reject) => {
      const task = uni.uploadFile({
        url: apiUrl,
        filePath: filePath,
        name: 'file',
        fileType: 'image',
        formData: { 'filename': fileName },
        header: { 'Content-Type': contentType },
        success: (uploadRes) => {
          if (uploadRes.statusCode === 200) {
            getAnalysisResultUnified(fileName, isForPrevious).then(resolve).catch(reject);
          } else {
            reject(new Error(`上传失败，状态码: ${uploadRes.statusCode}`));
          }
        },
        fail: (err) => {
          reject(new Error(`上传失败: ${err.errMsg}`));
        }
      });
      
      task.onProgressUpdate(function(res) {
        updateStatus(`上传中 ${res.progress}%`);
      });
    });
    
  } catch (err) {
    handleError(err, '上传失败', '上传失败: ' + err.message);
  }
}

// 统一的分析结果获取函数
async function getAnalysisResultUnified(fileName, isForPrevious = false) {
  try {
    updateStatus('分析中...');
    
    const analysisUrl = `https://apps.hundao.xyz/1_MiscarryCalc/analysis/${fileName}`;
    
    const res = await uni.request({
      url: analysisUrl,
      method: 'GET',
      timeout: 60000
    });

    if (res.statusCode === 200 && res.data) {
      // 根据类型选择对应的结果引用
      const targetRef = isForPrevious ? prevAnalysisResult : analysisResult;
      calculateAnalysisResults(res.data, targetRef);
      updateStatus('分析完成');
      return true;
    } else {
      throw new Error(`分析失败，状态码: ${res.statusCode}`);
    }
  } catch (err) {
    handleError(err, '获取分析结果失败', '分析失败: ' + err.message);
    throw err;
  }
}

// 分析结果计算
async function calculateAnalysisResults(result, refs) {
  refs.value = result;
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
  refs.value.GA0 = GA0 ? GA0.toFixed(2) : '-';
  refs.value.GA1 = GA1 ? GA1.toFixed(2) : '-';
  refs.value.GA2 = GA2 ? GA2.toFixed(2) : '-';
  refs.value.GA3 = GA3 ? GA3.toFixed(2) : '-';
}

// 日期格式化函数
function formatDate(dateString) {
  if (!dateString || dateString === '-') return '-';
  
  // 尝试解析各种日期格式
  let date;
  
  // 如果是已经格式化的日期（如"1月10日"），直接返回
  if (/\d+月\d+日/.test(dateString)) {
    return dateString;
  }
  
  // 尝试解析 YYYY-MM-DD、YYYY/MM/DD 等格式
  if (/^\d{4}[-/]\d{1,2}[-/]\d{1,2}$/.test(dateString)) {
    date = new Date(dateString);
  }
  // 尝试解析 DD/MM/YYYY 格式
  else if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(dateString)) {
    const parts = dateString.split('/');
    date = new Date(parts[2], parts[1] - 1, parts[0]);
  }
  // 尝试解析其他格式
  else {
    date = new Date(dateString);
  }
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    return dateString; // 如果无法解析，返回原始字符串
  }
  
  const month = date.getMonth() + 1;
  const day = date.getDate();
  
  return `${month}月${day}日`;
}

// 周数转换为"周+天"格式的函数
function formatWeeksAndDays(weekValue) {
  if (!weekValue || weekValue === '-') return '-';
  
  const totalWeeks = parseFloat(weekValue);
  if (isNaN(totalWeeks)) return '-';
  
  const weeks = Math.floor(totalWeeks);
  const days = Math.floor((totalWeeks - weeks) * 7);
  
  return `${weeks}周+${days}天`;
}

// 切换Robinson公式显示格式
function toggleRobinsonFormat() {
  showWeeksAndDays.value = !showWeeksAndDays.value;
}

// 计算受孕日期（根据超声检查日期和孕周）
function calculateConceptionDate(examDate, gestationalWeeks) {
  if (!examDate || !gestationalWeeks || gestationalWeeks === '-') return '-';
  
  try {
    const weeks = parseFloat(gestationalWeeks);
    if (isNaN(weeks)) return '-';
    
    // 解析检查日期
    let checkDate;
    if (/^\d{4}[-/]\d{1,2}[-/]\d{1,2}$/.test(examDate)) {
      checkDate = new Date(examDate);
    } else if (/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(examDate)) {
      const parts = examDate.split('/');
      checkDate = new Date(parts[2], parts[1] - 1, parts[0]);
    } else {
      checkDate = new Date(examDate);
    }
    
    if (isNaN(checkDate.getTime())) return '-';
    
    // 孕周转换为天数，然后从检查日期减去得到受孕日期
    const daysFromConception = weeks * 7;
    const conceptionDate = new Date(checkDate.getTime() - daysFromConception * 24 * 60 * 60 * 1000);
    
    const month = conceptionDate.getMonth() + 1;
    const day = conceptionDate.getDate();
    
    return `${month}月${day}日`;
  } catch (err) {
    console.error('计算受孕日期失败:', err);
    return '-';
  }
}

// 计算停育日期（根据受孕日期和当前报告的孕周）
function calculateMiscarryDate(conceptionDateStr, currentGestationalWeeks) {
  if (!conceptionDateStr || !currentGestationalWeeks || conceptionDateStr === '-' || currentGestationalWeeks === '-') return '-';
  
  try {
    const weeks = parseFloat(currentGestationalWeeks);
    if (isNaN(weeks)) return '-';
    
    // 解析受孕日期 - 假设是当年的日期
    const currentYear = new Date().getFullYear();
    const monthDayMatch = conceptionDateStr.match(/(\d+)月(\d+)日/);
    if (!monthDayMatch) return '-';
    
    const month = parseInt(monthDayMatch[1]) - 1; // JavaScript月份从0开始
    const day = parseInt(monthDayMatch[2]);
    
    const conceptionDate = new Date(currentYear, month, day);
    
    // 根据当前孕周计算停育日期
    const daysFromConception = weeks * 7;
    const miscarryDate = new Date(conceptionDate.getTime() + daysFromConception * 24 * 60 * 60 * 1000);
    
    const miscarryMonth = miscarryDate.getMonth() + 1;
    const miscarryDay = miscarryDate.getDate();
    
    return `${miscarryMonth}月${miscarryDay}日`;
  } catch (err) {
    console.error('计算停育日期失败:', err);
    return '-';
  }
}

// 计算预自然流产日期（停育日期 + 23天）
function calculateNaturalMiscarryDate(miscarryDateStr) {
  if (!miscarryDateStr || miscarryDateStr === '-') return '-';
  
  try {
    // 解析停育日期 - 假设是当年的日期
    const currentYear = new Date().getFullYear();
    const monthDayMatch = miscarryDateStr.match(/(\d+)月(\d+)日/);
    if (!monthDayMatch) return '-';
    
    const month = parseInt(monthDayMatch[1]) - 1; // JavaScript月份从0开始
    const day = parseInt(monthDayMatch[2]);
    
    const miscarryDate = new Date(currentYear, month, day);
    
    // 加上23天
    const naturalMiscarryDate = new Date(miscarryDate.getTime() + 23 * 24 * 60 * 60 * 1000);
    
    const naturalMiscarryMonth = naturalMiscarryDate.getMonth() + 1;
    const naturalMiscarryDay = naturalMiscarryDate.getDate();
    
    return `${naturalMiscarryMonth}月${naturalMiscarryDay}日`;
  } catch (err) {
    console.error('计算预自然流产日期失败:', err);
    return '-';
  }
}

// 统一的测试方法
async function executeTest(testType) {
  const testConfig = {
    'normal': {
      imageUrl: 'https://apps.hundao.xyz/rendered/B08.jpg',
      apiUrl: 'https://apps.hundao.xyz/1_MiscarryCalc/analysis/test',
      resultRef: analysisResult,
      imageRef: imageUrl
    },
    'miscarry': {
      imageUrl: 'https://apps.hundao.xyz/rendered/B02.jpg',
      apiUrl: 'https://apps.hundao.xyz/1_MiscarryCalc/analysis/test2',
      resultRef: analysisResult,
      imageRef: imageUrl
    },
    'previous': {
      imageUrl: 'https://apps.hundao.xyz/rendered/B01.jpg',
      apiUrl: 'https://apps.hundao.xyz/1_MiscarryCalc/analysis/test3',
      resultRef: prevAnalysisResult,
      imageRef: prevImageUrl
    }
  };

  const config = testConfig[testType];
  if (!config) {
    showToast('无效的测试类型');
    return;
  }

  try {
    updateStatus('测试中...');
    config.imageRef.value = config.imageUrl;
    
    const res = await uni.request({
      url: config.apiUrl,
      method: 'GET',
      timeout: 30000
    });
    
    if (res.statusCode === 200) {
      calculateAnalysisResults(res.data, config.resultRef);
      updateStatus('测试完成');
    } else {
      updateStatus('测试失败');
      showToast('测试失败');
    }
  } catch (err) {
    updateStatus('测试异常');
    showToast('测试异常');
  }
}

// 测试函数
async function testAnalysis() {
  await executeTest('normal');
}

async function testAnalysis2() {
  await executeTest('miscarry');
}

async function testAnalysis3() {
  await executeTest('previous');
}
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
	font-size: 32rpx;
	font-weight: 600;
	color: #ff6b35;
	margin-bottom: 20rpx;
	text-align: center;
	text-shadow: 0 1rpx 2rpx rgba(255, 107, 53, 0.2);
}

/* 上传区域 */
.upload-section {
	display: flex;
  flex-direction: column;
	justify-content: center;
  gap: 20rpx;
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
	padding: 16rpx;
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
	background: #fafbfc;
	border-radius: 16rpx;
	padding: 20rpx;
	border: 1rpx solid #e9ecef;
}

.result-list {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.result-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 24rpx;
	background-color: #f7f9fc;
	border-radius: 12rpx;
	padding: 18rpx 16rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
	margin-bottom: 8rpx;
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

/* 对比分析样式 */
.comparison-section {
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.comparison-header {
	text-align: center;
}

/* 图片对比区域 */
.comparison-images {
	display: flex;
	gap: 16rpx;
	background: #f8f9fa;
	border-radius: 16rpx;
	padding: 16rpx;
}

.image-column {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.column-title {
	font-size: 24rpx;
	font-weight: 600;
	color: #d4621a;
	text-align: center;
	margin-bottom: 12rpx;
	padding: 6rpx 12rpx;
	background: linear-gradient(45deg, #fef3e2, #fff0d6);
	border-radius: 16rpx;
	border: 1rpx solid #f5c99b;
}

/* 数据对比区域 */
.comparison-data {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
	background: #fafbfc;
	border-radius: 16rpx;
	padding: 20rpx;
	border: 1rpx solid #e9ecef;
}

.section-subtitle {
	font-size: 26rpx;
	font-weight: 600;
	color: #e8734c;
	text-align: center;
	margin-bottom: 15rpx;
	padding: 8rpx 0;
	background: linear-gradient(90deg, #fff5e6, #ffe8d1, #fff5e6);
	border-radius: 8rpx;
}

.comparison-row {
	display: flex;
	align-items: center;
	background-color: #f7f9fc;
	border-radius: 12rpx;
	padding: 18rpx 16rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
	margin-bottom: 8rpx;
}

.row-label {
	flex: 2.2;
	font-size: 24rpx;
	color: #666;
	font-weight: 600;
	line-height: 1.3;
}

.row-value {
	flex: 1;
	font-size: 24rpx;
	color: #333;
	text-align: center;
	font-weight: 600;
	line-height: 1.3;
	word-break: break-all;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

/* 对比模式下的分隔线 */
.comparison-row .row-value:first-of-type {
	border-right: 2rpx solid #e8ebf0;
	margin-right: 12rpx;
	padding-right: 12rpx;
}

/* 单列模式下右对齐 */
.result-item .row-value {
	text-align: right;
}

/* 单个报告样式 */
.single-report-data {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
	margin-bottom: 24rpx;
}

/* 可点击行样式 */
.clickable-row {
	cursor: pointer;
	transition: all 0.2s ease-in-out;
	position: relative;
}

.clickable-row::after {
	content: '👆';
	position: absolute;
	right: 8rpx;
	top: 50%;
	transform: translateY(-50%);
	font-size: 20rpx;
	opacity: 0.6;
}

.clickable-row:hover {
	background-color: #e8f4fd !important;
	transform: translateY(-2rpx);
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1) !important;
}
</style>