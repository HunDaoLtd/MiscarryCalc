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
				<!-- 测试按钮 -->
				<view class="test-buttons">
					<button @click="executeTest('normal')" class="upload-btn test-btn">
						<view class="button-content">
							<text class="upload-icon">🧪</text>
							<text>非停测试</text>
						</view>
					</button>
					<button @click="executeTest('miscarry')" class="upload-btn test-btn">
						<view class="button-content">
							<text class="upload-icon">🧪</text>
							<text>停育测试</text>
						</view>
					</button>
				</view>
			</view>
			<view v-if="uploadStatus" class="status-message">测试用：{{ uploadStatus }}</view>

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
						<picker mode="date" :value="prevAnalysisResult['日期']" :end="endDate" @change="onDateChange($event, 'previous')" style="flex: 1; text-align: center;">
							<text class="row-value" :class="{ 'date-missing': !prevAnalysisResult['日期'], 'date-invalid': isDateOrderInvalid }">{{ formatDate(prevAnalysisResult['日期']) }} 🗓️</text>
						</picker>
            <text class="row-value">{{ formatDate(analysisResult['日期']) }}</text>
					</view>
				</view>

				<!-- 孕周估算对比 -->
				<view class="comparison-data">
					<text class="section-subtitle">孕周估算</text>
					<!-- 孕囊估算：当任一报告没有胚芽长时显示 -->
					<view v-if="!analysisResult['胚芽长'] || !prevAnalysisResult['胚芽长']" class="comparison-row clickable-row" @click="toggleRobinsonFormat">
						<text class="row-label">孕囊估算</text>
						<text class="row-value">{{ !prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA0) : (prevAnalysisResult.GA0 + ' 周')) : '-' }}</text>
						<text class="row-value">{{ !analysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA0) : (analysisResult.GA0 + ' 周')) : '-' }}</text>
					</view>
					<!-- Robinson公式等：当任一报告有胚芽长时显示 -->
					<view v-if="analysisResult['胚芽长'] || prevAnalysisResult['胚芽长']">
						<view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
							<text class="row-label">Robinson公式 (推荐)</text>
							<text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA1) : (prevAnalysisResult.GA1 + ' 周')) : '-' }}</text>
							<text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA1) : (analysisResult.GA1 + ' 周')) : '-' }}</text>
						</view>
            <view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
              <text class="row-label">Hadlock公式</text>
              <text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA4) : (prevAnalysisResult.GA4 + ' 周')) : '-' }}</text>
              <text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA4) : (analysisResult.GA4 + ' 周')) : '-' }}</text>
            </view>
						<view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
							<text class="row-label">回归方程</text>
							<text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA2) : (prevAnalysisResult.GA2 + ' 周')) : '-' }}</text>
							<text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA2) : (analysisResult.GA2 + ' 周')) : '-' }}</text>
						</view>
						<view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
							<text class="row-label">经验法则</text>
							<text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(prevAnalysisResult.GA3) : (prevAnalysisResult.GA3 + ' 周')) : '-' }}</text>
							<text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA3) : (analysisResult.GA3 + ' 周')) : '-' }}</text>
						</view>
					</view>
				</view>

        <!-- 停育分析 -->
         <view class="comparison-data">
					<text class="section-subtitle">停育分析</text>
					<view class="result-list">
						<view class="result-item">
							<text class="row-label">孕0天 (LMP)</text>
							<text class="row-value">{{ miscarryAnalysis.lastMenstrualPeriod }}</text>
						</view>
						<view class="result-item">
							<text class="row-label">停育日期</text>
							<text class="row-value">{{ miscarryAnalysis.miscarryDate }}</text>
						</view>
						<view class="result-item">
							<text class="row-label">预自然流产日</text>
							<text class="row-value">{{ miscarryAnalysis.naturalMiscarryDate }}</text>
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
						<view v-if="!analysisResult['胚芽长']" class="result-item clickable-row" @click="toggleRobinsonFormat">
							<text class="row-label">孕囊估算</text>
							<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA0) : (analysisResult.GA0 + ' 周') }}</text>
						</view>
						<view v-else>
							<view class="result-item clickable-row" @click="toggleRobinsonFormat">
								<text class="row-label">Robinson公式 (推荐)</text>
								<text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA1) : (analysisResult.GA1 + ' 周') }}</text>
							</view>
              <view class="result-item clickable-row" @click="toggleRobinsonFormat">
                <text class="row-label">Hadlock公式</text>
                <text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA4) : (analysisResult.GA4 + ' 周') }}</text>
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

        <!-- 如果停育，显示更多信息 -->
        <view v-if="analysisResult && analysisResult['是否停育']">
          <view class="single-report-data">
						<text class="section-subtitle">停育分析</text>
						<view class="result-list">
							<view class="result-item">
								<text class="row-label">孕0天 (LMP)</text>
								<text class="row-value">{{ '需分析停育前报告' }}</text>
							</view>
							<view class="result-item">
								<text class="row-label">停育日期</text>
								<text class="row-value">{{ '需分析停育前报告' }}</text>
							</view>
							<view class="result-item">
								<text class="row-label">预自然流产日</text>
								<text class="row-value">{{ '需分析停育前报告' }}</text>
							</view>
						</view>
            <!-- 上传胎停育前报告单按钮 -->
						<view class="action-buttons">
							<button @click="choosePrevImage" :loading="isPrevLoading" :disabled="isPrevLoading" class="upload-btn prev-btn">
								<view class="button-content">
									<text class="upload-icon">+</text>
									<text>{{ isPrevLoading ? '分析中...' : '拍摄胎停育前报告单' }}</text>
								</view>
							</button>
							<button @click="executeTest('previous')" class="upload-btn test-btn">
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
import { ref, computed } from 'vue';

const endDate = new Date().toISOString().split('T')[0];

// 响应式数据
const imageUrl = ref('');
const analysisResult = ref('');
const uploadStatus = ref('');
const isLoading = ref(false);

// 用于存储胎停育前的图片和分析结果
const prevImageUrl = ref('');
const prevAnalysisResult = ref('');

// 分别控制两个上传按钮的加载状态
const isPrevLoading = ref(false);

// 控制Robinson公式显示格式（true: 周+天格式, false: 周格式）
const showWeeksAndDays = ref(false);

// 新增：日期顺序校验
const isDateOrderInvalid = ref(false);
const hasShownInvalidDateToast = ref(false);
function validateDateOrder(showHint = true) {
  try {
    const prevDateStr = prevAnalysisResult.value && prevAnalysisResult.value['日期'];
    const currDateStr = analysisResult.value && analysisResult.value['日期'];
    if (!prevDateStr || !currDateStr) {
      isDateOrderInvalid.value = false;
      return;
    }
    const prevDate = new Date(prevDateStr);
    const currDate = new Date(currDateStr);
    if (isNaN(prevDate.getTime()) || isNaN(currDate.getTime())) {
      isDateOrderInvalid.value = false;
      return;
    }
    const invalid = currDate < prevDate;
    if (invalid && showHint && !hasShownInvalidDateToast.value) {
      showToast('当前报告日期早于停育前报告日期，请核对');
      hasShownInvalidDateToast.value = true;
    }
    if (!invalid) {
      hasShownInvalidDateToast.value = false; // 恢复以便后续再次提醒
    }
    isDateOrderInvalid.value = invalid;
  } catch (e) {
    // 忽略
  }
}

// 新增：统一获取不同报告（current/previous）的引用与前缀
function getReportRefs(kind = 'current') {
  return kind === 'previous'
    ? { imageRef: prevImageUrl, resultRef: prevAnalysisResult, prefix: 'prev_' }
    : { imageRef: imageUrl, resultRef: analysisResult, prefix: 'score_' };
}

// 计算属性：停育分析相关数据
const miscarryAnalysis = computed(() => {
  // 检查是否有必要的数据
  if (!prevAnalysisResult.value || !analysisResult.value) {
    return {
      lastMenstrualPeriod: '-',
      miscarryDate: '-',
      naturalMiscarryDate: '-'
    };
  }

  // 检查是否有日期和孕周数据
  const hasValidData = prevAnalysisResult.value['日期'] && 
                      prevAnalysisResult.value.GA1 && 
                      analysisResult.value.GA1;

  if (!hasValidData) {
    return {
      lastMenstrualPeriod: '需要红字日期！',
      miscarryDate: '需要红字日期！',
      naturalMiscarryDate: '需要红字日期！'
    };
  }

  // 计算末次月经
  const lastMenstrualPeriod = calculatelastMenstrualPeriod(prevAnalysisResult.value['日期'], prevAnalysisResult.value.GA1);
  
  // 计算停育日期
  const miscarryDate = calculateMiscarryDate(lastMenstrualPeriod, analysisResult.value.GA1);
  
  // 计算预自然流产日期
  const naturalMiscarryDate = calculateNaturalMiscarryDate(miscarryDate);

  return {
    lastMenstrualPeriod,
    miscarryDate,
    naturalMiscarryDate
  };
});

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

// 统一的图片选择函数（以 kind 区分 current/previous）
async function chooseImageUnified(kind = 'current') {
  try {
    updateStatus('选择文件中...');

    const res = await uni.chooseImage({
      count: 1,
      sourceType: ['album', 'camera'],
      sizeType: ['compressed']
    });

    const filePath = res.tempFilePaths[0];

    const { imageRef } = getReportRefs(kind);
    imageRef.value = filePath;

    // 根据类型设置对应的 loading 状态
    if (kind === 'previous') {
      isPrevLoading.value = true;
    } else {
      isLoading.value = true;
    }
    
    const { ext, contentType } = getFileTypeInfo(filePath);
    await uploadFileUnified(filePath, contentType, ext, kind);
  } catch (err) {
    handleError(err, '选择文件失败', '选择文件失败');
  } finally {
    // 根据类型重置对应的 loading 状态
    if (kind === 'previous') {
      isPrevLoading.value = false;
    } else {
      isLoading.value = false;
    }
  }
}

// 选择主报告单
async function chooseImage() {
  await chooseImageUnified('current');
}

// 选择胎停育前报告单
async function choosePrevImage() {
  await chooseImageUnified('previous');
}

// 统一的文件上传函数（以 kind 区分 current/previous）
async function uploadFileUnified(filePath, contentType, ext, kind = 'current') {
  if (!ext) ext = '.jpg';
  try {
    updateStatus('上传中...');

    const { resultRef, prefix } = getReportRefs(kind);
    resultRef.value = '';

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
            getAnalysisResultUnified(fileName, kind).then(resolve).catch(reject);
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

// 统一的分析结果获取函数（以 kind 区分 current/previous）
async function getAnalysisResultUnified(fileName, kind = 'current') {
  try {
    updateStatus('分析中...');

    const analysisUrl = `https://apps.hundao.xyz/1_MiscarryCalc/analysis/${fileName}`;

    const res = await uni.request({
      url: analysisUrl,
      method: 'GET',
      timeout: 60000
    });

    if (res.statusCode === 200 && res.data) {
      console.log(kind, '分析结果:', res.data);
      const { resultRef } = getReportRefs(kind);
      calculateAnalysisResults(res.data, resultRef);
      validateDateOrder(true);
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
  const GS = parseInt(result["孕囊大小"]);
  const CRL = parseInt(result["胚芽长"]);
  const CRL_cm = CRL / 10; // 转换为厘米
  let GA0, GA1, GA2, GA3, GA4;
  if (GS !== undefined && GS !== null) GA0 = (0.882 * GS + 33.117) / 7; // 0. 孕囊估算（适用于5-6周前的早期评估）
  if (CRL !== undefined && CRL !== null) {
    GA1 = (8.052 * Math.pow(CRL * 1.037, 0.5) + 23.73) / 7;             // 1. Robinson公式（国际公认标准方法）
    GA2 = 5.2876 + (0.1584 * CRL) - (0.0007 * Math.pow(CRL, 2));        // 2. 回归方程（其他研究提出）
    GA3 = CRL / 10 + 6.5;                                               // 3. 经验法则（简易快速估算）
    // 4. crown–rump length from Hadlock et al.
    GA4 = Math.exp(1.685 + 0.316 * CRL_cm - 0.049 * Math.pow(CRL_cm, 2) + 0.004 * Math.pow(CRL_cm, 3) - 0.0001 * Math.pow(CRL_cm, 4));
  }
  refs.value.GA0 = GA0 ? GA0.toFixed(2) : '-';
  refs.value.GA1 = GA1 ? GA1.toFixed(2) : '-';
  refs.value.GA2 = GA2 ? GA2.toFixed(2) : '-';
  refs.value.GA3 = GA3 ? GA3.toFixed(2) : '-';
  refs.value.GA4 = GA4 ? GA4.toFixed(2) : '-';
}

// 日期格式化函数
function formatDate(dateString) {
  if (!dateString || dateString === '-') return '未识别到日期';

  try {
    // 直接解析YYYY-MM-DD格式，转换为"月日"格式
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '未识别到日期';
    
    const month = date.getMonth() + 1;
    const day = date.getDate();
    
    return `${month}月${day}日`;
  } catch (err) {
    return dateString; // 解析失败返回原字符串
  }
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

// 手动修改日期
function onDateChange(e, kind) {
  const { resultRef } = getReportRefs(kind);
  if (resultRef.value) {
    resultRef.value['日期'] = e.detail.value;
  } else {
    // 如果还没有分析结果，初始化一个
    if (kind === 'current') {
      analysisResult.value = { '日期': e.detail.value };
    } else if (kind === 'previous') {
      prevAnalysisResult.value = { '日期': e.detail.value };
    }
  }
  validateDateOrder(true);
}

// 计算末次月经（根据超声检查日期和孕周）
function calculatelastMenstrualPeriod(examDate, gestationalWeeks) {
  if (!examDate || !gestationalWeeks || gestationalWeeks === '-') return '-';
  
  try {
    const weeks = parseFloat(gestationalWeeks);
    if (isNaN(weeks)) return '-';
    
    // 直接解析YYYY-MM-DD格式日期
    const checkDate = new Date(examDate);
    if (isNaN(checkDate.getTime())) return '-';
    
    // 孕周转换为天数，然后从检查日期减去得到末次月经
    const daysFromlastMenstrual = weeks * 7;
    const lastMenstrualPeriod = new Date(checkDate.getTime() - daysFromlastMenstrual * 24 * 60 * 60 * 1000);
    
    const year = lastMenstrualPeriod.getFullYear();
    const month = String(lastMenstrualPeriod.getMonth() + 1).padStart(2, '0');
    const day = String(lastMenstrualPeriod.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
  } catch (err) {
    console.error('计算末次月经失败:', err);
    return '-';
  }
}

// 计算停育日期（根据末次月经和当前报告的孕周）
function calculateMiscarryDate(lastMenstrualPeriodStr, currentGestationalWeeks) {
  if (!lastMenstrualPeriodStr || !currentGestationalWeeks || lastMenstrualPeriodStr === '-' || currentGestationalWeeks === '-') return '-';
  
  try {
    const weeks = parseFloat(currentGestationalWeeks);
    if (isNaN(weeks)) return '-';
    
    // 直接解析YYYY-MM-DD格式的末次月经
    const lastMenstrualPeriod = new Date(lastMenstrualPeriodStr);
    if (isNaN(lastMenstrualPeriod.getTime())) return '-';
    
    // 根据当前孕周计算停育日期
    const daysFromlastMenstrual = weeks * 7;
    const miscarryDate = new Date(lastMenstrualPeriod.getTime() + daysFromlastMenstrual * 24 * 60 * 60 * 1000);
    
    const year = miscarryDate.getFullYear();
    const month = String(miscarryDate.getMonth() + 1).padStart(2, '0');
    const day = String(miscarryDate.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
  } catch (err) {
    console.error('计算停育日期失败:', err);
    return '-';
  }
}

// 计算预自然流产日期（停育日期 + 23天）
function calculateNaturalMiscarryDate(miscarryDateStr) {
  if (!miscarryDateStr || miscarryDateStr === '-') return '-';
  
  try {
    // 直接解析YYYY-MM-DD格式的停育日期
    const miscarryDate = new Date(miscarryDateStr);
    if (isNaN(miscarryDate.getTime())) return '-';
    
    // 加上23天
    const naturalMiscarryDate = new Date(miscarryDate.getTime() + 23 * 24 * 60 * 60 * 1000);
    
    const year = naturalMiscarryDate.getFullYear();
    const month = String(naturalMiscarryDate.getMonth() + 1).padStart(2, '0');
    const day = String(naturalMiscarryDate.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
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
      apiUrl: 'https://apps.hundao.xyz/1_MiscarryCalc/analysis/test6',
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
      validateDateOrder(true);
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

/* 测试按钮组 */
.test-buttons {
	display: flex;
	gap: 20rpx;
}

/* 操作按钮组 */
.action-buttons {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
	margin-top: 20rpx;
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

/* 测试按钮样式 */
.test-btn {
	background: linear-gradient(45deg, #ffd966, #f6b26b) !important;
	box-shadow: 0 8rpx 20rpx rgba(255, 182, 107, 0.3) !important;
}

/* 停育前报告按钮样式 */
.prev-btn {
	background: linear-gradient(45deg, #b6b9ff, #e3d9fa) !important;
	box-shadow: 0 8rpx 20rpx rgba(182, 185, 255, 0.3) !important;
}

.upload-btn::after { border: none; }

.upload-btn[disabled] {
	opacity: 0.7;
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

/* 统一：卡片容器通用样式（原 result-section 与 comparison-data 公共部分） */
.result-section,
.comparison-data {
	display: flex;
	flex-direction: column;
	background: #fafbfc;
	border-radius: 16rpx;
	padding: 20rpx;
	border: 1rpx solid #e9ecef;
}

/* comparison-data 额外的内部间距（gap） */
.comparison-data { gap: 12rpx; }

/* 区域内列表（原 result-list 与 single-report-data 公共部分） */
.result-list,
.single-report-data {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

/* single-report-data 原有的额外外边距 */
.single-report-data { margin-bottom: 24rpx; }

/* 行容器通用样式（原 result-item 与 comparison-row 公共部分） */
.result-item,
.comparison-row {
	display: flex;
	align-items: center;
	background-color: #f7f9fc;
	border-radius: 12rpx;
	padding: 18rpx 16rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
	margin-bottom: 8rpx;
}

/* result-item 特有：两端对齐 */
.result-item { justify-content: space-between; }

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

.row-label {
	flex: 1.8;
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
	word-break: break-word;
	white-space: normal;
	overflow: visible;
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

/* 日期缺失提醒样式 */
.date-missing {
	color: #e74c3c !important;
	font-weight: bold !important;
	background: linear-gradient(45deg, #ffebee, #ffcdd2) !important;
	padding: 4rpx 8rpx !important;
	border-radius: 8rpx !important;
	border: 1rpx solid #ffcdd2 !important;
	position: relative;
	cursor: pointer;
}

.date-missing::before {
	content: '⚠️';
	margin-right: 4rpx;
}

/* 新增：日期顺序异常标红 */
.date-invalid {
	color: #e53935 !important;
	font-weight: bold !important;
	border-bottom: 2rpx solid #e53935;
}

/* 数据缺失提醒样式 */
.data-missing {
	color: #ff9800 !important;
	font-weight: bold !important;
	background: linear-gradient(45deg, #fff3e0, #ffe0b2) !important;
	padding: 4rpx 8rpx !important;
	border-radius: 8rpx !important;
	border: 1rpx solid #ffe0b2 !important;
	position: relative;
}

.data-missing::before {
	content: '⚠️';
	margin-right: 4rpx;
}
</style>