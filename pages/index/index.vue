<!-- 有大量未审计的AI代码 -->
<template>
  <view class="container">
    <view class="content-card">
      <view class="upload-section">
        <!-- 当前报告文件选择 -->
        <uni-file-picker v-if="!isLoading" class="picker-btn-wrapper" limit="1" file-mediatype="image"
          @select="onFileSelectCurrent">
          <button class="upload-btn" :disabled="isLoading">
            <view class="button-content">
              <text class="upload-icon">+</text>
              <text>拍摄 / 选择超声报告单</text>
            </view>
          </button>
        </uni-file-picker>
        <!-- 加载中显示进度条 -->
        <button class="upload-btn" :disabled="true" v-else>
          <view class="button-content progress-mode">
            <view class="progress-wrapper">
              <text class="progress-text">分析中 {{ analysisProgressCurrent }}%</text>
              <view class="progress-bar">
                <view class="progress-bar-inner" :style="{ width: analysisProgressCurrent + '%' }"></view>
              </view>
            </view>
          </view>
        </button>
        <!-- 测试按钮 -->
        <!-- <view class="test-buttons">
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
				</view> -->
      </view>
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
            <picker mode="date" :value="prevAnalysisResult['日期']" :end="endDate"
              @change="onDateChange($event, 'previous')" style="flex: 1; text-align: center;">
              <text class="row-value"
                :class="{ 'date-missing': !prevAnalysisResult['日期'], 'date-invalid': isDateOrderInvalid }">{{
                  formatDate(prevAnalysisResult['日期']) }} 🗓️</text>
            </picker>
            <text class="row-value">{{ formatDate(analysisResult['日期']) }}</text>
          </view>
        </view>

        <!-- 孕周估算对比 -->
        <view class="comparison-data">
          <text class="section-subtitle">孕周估算</text>
          <!-- 孕囊估算：当任一报告没有胚芽长时显示 -->
          <view v-if="!analysisResult['胚芽长'] || !prevAnalysisResult['胚芽长']" class="comparison-row clickable-row"
            @click="toggleRobinsonFormat">
            <text class="row-label">孕囊估算</text>
            <text class="row-value">{{ !prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ?
              formatWeeksAndDays(prevAnalysisResult.GA0) : (prevAnalysisResult.GA0 + ' 周')) : '-' }}</text>
            <text class="row-value">{{ !analysisResult['胚芽长'] ? (showWeeksAndDays ?
              formatWeeksAndDays(analysisResult.GA0) : (analysisResult.GA0 + ' 周')) : '-' }}</text>
          </view>
          <!-- Robinson公式等：当任一报告有胚芽长时显示 -->
          <view v-if="analysisResult['胚芽长'] || prevAnalysisResult['胚芽长']">
            <view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
              <text class="row-label">Robinson公式 (推荐)</text>
              <text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(prevAnalysisResult.GA1) : (prevAnalysisResult.GA1 + ' 周')) : '-' }}</text>
              <text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(analysisResult.GA1) : (analysisResult.GA1 + ' 周')) : '-' }}</text>
            </view>
            <view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
              <text class="row-label">Hadlock公式</text>
              <text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(prevAnalysisResult.GA4) : (prevAnalysisResult.GA4 + ' 周')) : '-' }}</text>
              <text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(analysisResult.GA4) : (analysisResult.GA4 + ' 周')) : '-' }}</text>
            </view>
            <view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
              <text class="row-label">回归方程</text>
              <text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(prevAnalysisResult.GA2) : (prevAnalysisResult.GA2 + ' 周')) : '-' }}</text>
              <text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(analysisResult.GA2) : (analysisResult.GA2 + ' 周')) : '-' }}</text>
            </view>
            <view class="comparison-row clickable-row" @click="toggleRobinsonFormat">
              <text class="row-label">经验法则</text>
              <text class="row-value">{{ prevAnalysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(prevAnalysisResult.GA3) : (prevAnalysisResult.GA3 + ' 周')) : '-' }}</text>
              <text class="row-value">{{ analysisResult['胚芽长'] ? (showWeeksAndDays ?
                formatWeeksAndDays(analysisResult.GA3) : (analysisResult.GA3 + ' 周')) : '-' }}</text>
            </view>
          </view>
        </view>

        <!-- 停育分析 -->
        <view class="comparison-data">
          <text class="section-subtitle">停育分析</text>
          <view class="result-list">
            <view class="result-item">
              <text class="row-label">孕0天 (LMP)</text>
              <text class="row-value">{{ formatYMD(miscarryAnalysis.lastMenstrualPeriod) }}</text>
            </view>
            <view class="result-item">
              <text class="row-label">停育日期</text>
              <text class="row-value">{{ formatYMD(miscarryAnalysis.miscarryDate) }}</text>
            </view>
            <view class="result-item clickable-row" @click="showNaturalMiscarryModal">
              <text class="row-label">预自然流产日</text>
              <text class="row-value">{{ formatYMD(miscarryAnalysis.naturalMiscarryDate) }}</text>
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
              <text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA0) : (analysisResult.GA0
                + ' 周') }}</text>
            </view>
            <view v-else>
              <view class="result-item clickable-row" @click="toggleRobinsonFormat">
                <text class="row-label">Robinson公式 (推荐)</text>
                <text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA1) :
                  (analysisResult.GA1 + ' 周') }}</text>
              </view>
              <view class="result-item clickable-row" @click="toggleRobinsonFormat">
                <text class="row-label">Hadlock公式</text>
                <text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA4) :
                  (analysisResult.GA4 + ' 周') }}</text>
              </view>
              <view class="result-item clickable-row" @click="toggleRobinsonFormat">
                <text class="row-label">回归方程</text>
                <text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA2) :
                  (analysisResult.GA2 + ' 周') }}</text>
              </view>
              <view class="result-item clickable-row" @click="toggleRobinsonFormat">
                <text class="row-label">经验法则</text>
                <text class="row-value">{{ showWeeksAndDays ? formatWeeksAndDays(analysisResult.GA3) :
                  (analysisResult.GA3 + ' 周') }}</text>
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
              <view class="result-item clickable-row" @click="showNaturalMiscarryModal">
                <text class="row-label">预自然流产日</text>
                <text class="row-value">{{ '需分析停育前报告' }}</text>
              </view>
            </view>
            <!-- 上传胎停育前报告单 -->
            <view class="action-buttons">
              <uni-file-picker v-if="!isPrevLoading" class="picker-btn-wrapper" limit="1" file-mediatype="image"
                @select="onFileSelectPrevious">
                <button class="upload-btn prev-btn" :disabled="isPrevLoading">
                  <view class="button-content">
                    <text class="upload-icon">+</text>
                    <text>拍摄 / 选择胎停育前报告单</text>
                  </view>
                </button>
              </uni-file-picker>
              <button class="upload-btn prev-btn" :disabled="true" v-else>
                <view class="button-content progress-mode">
                  <view class="progress-wrapper">
                    <text class="progress-text">分析中 {{ analysisProgressPrev }}%</text>
                    <view class="progress-bar">
                      <view class="progress-bar-inner" :style="{ width: analysisProgressPrev + '%' }"></view>
                    </view>
                  </view>
                </view>
              </button>
              <!-- 测试按钮 -->
              <!-- <button @click="executeTest('previous')" class="upload-btn test-btn">
								<view class="button-content">
									<text class="upload-icon">+</text>
									<text>胎停育前测试</text>
								</view>
							</button> -->
            </view>
          </view>
        </view>

      </view>
    </view>

    <!-- 自然流产概率 自定义弹窗 -->
    <uni-popup ref="naturalPopup" type="center">
      <view class="custom-dialog">
        <text class="section-title">自然流产概率</text>
        <view class="comparison-data">
          <view v-for="(item, idx) in naturalData" :key="idx" class="result-item">
            <text class="row-label">{{ item.label }}</text>
            <text class="row-value">{{ item.value }}</text>
          </view>
        </view>
        <view class="dialog-actions">
          <button class="dialog-btn" @click="closeNaturalPopup">知道了</button>
        </view>
      </view>
    </uni-popup>

    <!-- 页脚 -->
    <view class="page-footer">
      <text class="footer-line">1、仅适用于孕早期（前14周内）。\n</text>
      <text class="footer-line">2、计算结果仅供参考，不提供医疗诊断或治疗建议。</text>
      <view class="footer-line" @click="openExternal('https://zhuanlan.zhihu.com/p/18132159339')">
        <text class="footer-link">3、自然流产科普知识点我。</text>
      </view>
      <text class="footer-line meta">© 2025 魂道 MiscarryCalc · v1.1.0</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';

const API_BASE = 'https://apps.hundao.xyz/1_miscarry_calc';

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

// 计算属性：停育分析相关数据（使用 Date 对象进行内部运算）
const miscarryAnalysis = computed(() => {
  if (!prevAnalysisResult.value || !analysisResult.value) {
    return {
      lastMenstrualPeriod: null,
      miscarryDate: null,
      naturalMiscarryDate: null
    };
  }

  const hasValidData = prevAnalysisResult.value['日期'] &&
    prevAnalysisResult.value.GA1 &&
    analysisResult.value.GA1;

  if (!hasValidData) {
    return {
      lastMenstrualPeriod: null,
      miscarryDate: null,
      naturalMiscarryDate: null
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
  // console.log('Toast:', title, icon);
}
// 新增：跨平台打开外部链接
function openExternal(url) {
  // #ifdef H5
  window.open(url, '_blank');
  // #endif
  // #ifdef APP-PLUS
  try { plus.runtime.openURL(url); } catch (e) { uni.setClipboardData({ data: url }); showToast('已复制链接'); }
  // #endif
  // #ifdef MP-WEIXIN
  wx.setClipboardData({
    data: url,
    success() {
      uni.showModal({
        title: '提示',
        content: '小程序限制，已复制链接，请在浏览器中打开。',
        showCancel: false
      });
    }
  });
  // #endif
}

// 工具函数：统一的状态管理
function updateStatus(message) {
  uploadStatus.value = message;
  console.log('状态更新:', message);
}

// 工具函数：统一的错误处理
function handleError(error, defaultMessage, statusMessage, show=true) {
  console.error(defaultMessage, error);
  updateStatus(statusMessage || (defaultMessage + ': ' + error.message));
  if (show) {
    showToast(statusMessage || defaultMessage);
  }
}

// 工具函数：获取文件扩展名和内容类型
function getFileTypeInfo(filePath) {
  const ext = filePath.substring(filePath.lastIndexOf('.')).toLowerCase();
  let contentType = 'application/octet-stream';
  const typeMap = { '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.bmp': 'image/bmp', '.webp': 'image/webp', '.avif': 'image/avif' };
  contentType = typeMap[ext] || contentType;
  return { ext, contentType };
}

// ====== 新增：图片压缩相关工具 ======
const MAX_UPLOAD_SIZE = 1024 * 1024; // 1M
const QUALITY_STEPS = [80, 70, 60, 50, 40, 30];

async function compressNativeLoop(path) {
  // 仅 App / 小程序平台可用
  let currentPath = path;
  for (const q of QUALITY_STEPS) {
    try {
      const r = await uni.compressImage({ src: currentPath, quality: q });
      const newPath = (r.tempFilePath || r.tempFiles && r.tempFiles[0] && r.tempFiles[0].path) || r;
      if (!newPath) continue;
      const info = await uni.getFileInfo({ filePath: newPath });
      currentPath = newPath;
      if (info.size <= MAX_UPLOAD_SIZE) {
        return { path: currentPath, size: info.size, hitLimit: true };
      }
    } catch (e) {
      // 压缩失败则继续尝试下一个质量
      console.warn('compressImage 失败(quality=' + q + '):', e);
    }
  }
  try {
    const info = await uni.getFileInfo({ filePath: currentPath });
    return { path: currentPath, size: info.size, hitLimit: info.size <= MAX_UPLOAD_SIZE };
  } catch { return { path: currentPath, size: NaN, hitLimit: false }; }
}

// H5 压缩：使用 canvas 逐步降低质量；可同时按最大宽度限制
async function compressH5File(file, maxWidth = 1600) {
  const createImage = (file) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = URL.createObjectURL(file);
  });
  function dataURLToFile(dataURL, filename) {
    const arr = dataURL.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length; const u8arr = new Uint8Array(n);
    while (n--) u8arr[n] = bstr.charCodeAt(n);
    return new File([u8arr], filename, { type: mime });
  }
  const img = await createImage(file);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  let { width, height } = img;
  if (width > maxWidth) {
    const ratio = maxWidth / width; width = maxWidth; height = Math.round(height * ratio);
  }
  canvas.width = width; canvas.height = height; ctx.drawImage(img, 0, 0, width, height);

  let outFile = file;
  for (const q of [0.8, 0.7, 0.6, 0.5, 0.4, 0.32, 0.28]) {
    const dataURL = canvas.toDataURL('image/jpeg', q);
    const f2 = dataURLToFile(dataURL, file.name.replace(/\.[^.]+$/, '') + '_c.jpg');
    if (f2.size <= MAX_UPLOAD_SIZE) { outFile = f2; break; }
    outFile = f2; // 继续循环尝试更低质量
  }
  return outFile;
}

// 文件选择回调（当前报告）
function onFileSelectCurrent(e) {
  handleFileSelect(e, 'current');
}
// 文件选择回调（停育前报告）
function onFileSelectPrevious(e) {
  handleFileSelect(e, 'previous');
}

async function handleFileSelect(e, kind) {
  try {
    const files = e.tempFiles || [];
    if (!files.length) { showToast('未选择文件'); return; }
    let f = files[0];
    const { imageRef, resultRef } = getReportRefs(kind);
    let originalPath = f.path || f.url || '';
    let uploadPath = originalPath;
    let uploadFileObj = f.file || null; // H5 File 对象（若存在）
    const originalSize = f.size; // 可能为 undefined (某些平台)

    const rawName = f.name || f.url || originalPath || 'image.jpg';
    const { ext, contentType } = getFileTypeInfo(rawName);

    if (kind === 'previous') { isPrevLoading.value = true; startProgress('previous'); } else { isLoading.value = true; startProgress('current'); }

    imageRef.value = uploadPath; // 先展示原图

    // 超过限制尝试压缩
    if (originalSize && originalSize > MAX_UPLOAD_SIZE) {
      updateStatus('压缩中...');
      let compressedOk = false;
      if (uploadFileObj && typeof window !== 'undefined') {
        try {
          const compressedFile = await compressH5File(uploadFileObj);
          if (compressedFile && compressedFile.size < uploadFileObj.size) {
            uploadFileObj = compressedFile;
            imageRef.value = URL.createObjectURL(compressedFile);
            compressedOk = compressedFile.size <= MAX_UPLOAD_SIZE;
          }
        } catch (err) { console.warn('H5 压缩失败，使用原图', err); }
      } else {
        try {
          const r = await compressNativeLoop(uploadPath);
          uploadPath = r.path;
          imageRef.value = uploadPath;
          if (r.hitLimit) compressedOk = true;
        } catch (err) { console.warn('Native 压缩失败，使用原图', err); }
      }
      showToast(compressedOk ? '压缩完成' : '已尝试压缩');
    }

    // 必须取得哈希
    const hashHex = await computeImageHashHex(uploadPath, uploadFileObj);
    if (!hashHex) {
      showToast('哈希计算失败，请重试');
      return;
    }
    const fileName = `${hashHex}${ext}`;

    // 查重
    let existedRecord = null;
    try { existedRecord = await checkExists(fileName); } catch (checkErr) { console.warn('查重失败, 忽略继续上传', checkErr); }
    if (existedRecord) {
      updateStatus('已存在，跳过上传');
      showToast('已存在，跳过上传');
      if (existedRecord.analysis) {
        console.log('使用已有分析结果:', existedRecord.analysis);
        calculateAnalysisResults(existedRecord.analysis, resultRef);
        validateDateOrder(true);
        if (kind === 'previous') { analysisProgressPrev.value = 99; setTimeout(() => stopProgress('previous'), 300); }
        else { analysisProgressCurrent.value = 99; setTimeout(() => stopProgress('current'), 300); }
      } else {
        await processAnalysis(fileName, kind);
      }
      return;
    }

    // 重置结果占位
    resultRef.value = '';

    // 上传
    await uploadFileUnified(uploadPath, contentType, fileName, kind, uploadFileObj, hashHex);
    // 上传成功后再分析
    await processAnalysis(fileName, kind);
  } catch (err) {
    handleError(err, '选择文件失败', '选择文件失败', show=false);
  } finally {
    if (kind === 'previous') { isPrevLoading.value = false; }
    else { isLoading.value = false; }
    if (kind === 'previous' && progressTimerPrev) { stopProgress('previous'); }
    if (kind !== 'previous' && progressTimerCurrent) { stopProgress('current'); }
  }
}

// ------ 服务器是否已有相同图像(统一 fileName) ------
async function checkExists(fileName) {
  try {
    const res = await uni.request({
      url: `${API_BASE}/images/${fileName}`,
      method: 'GET',
      timeout: 15000
    });
    if (res && res.statusCode === 200) return res.data;
    if (res && res.statusCode === 404) return null;
    return null; // 其他状态当作不存在，不抛错以不中断流程
  } catch (e) {
    console.warn('查重异常，继续上传:', e);
    return null; // 出错也继续后续上传流程
  }
}

// 统一上传：fileName 已由 hash+ext 生成
async function uploadFileUnified(filePath, contentType, fileName, kind = 'current', fileObj = null, hashHex = null) {
  try {
    updateStatus('上传中...');
    showToast('上传中...');
    const apiUrl = `${API_BASE}/images/${fileName}`;

    if (fileObj && typeof File !== 'undefined' && fileObj instanceof File) {
      const formData = new FormData();
      formData.append('file', fileObj, fileName);
      formData.append('filename', fileName);
      formData.append('hash', hashHex);
      const resp = await fetch(apiUrl, { method: 'POST', body: formData });
      if (!resp.ok) { throw new Error('上传失败，状态码: ' + resp.status); }
      return true;
    } else {
      await new Promise((resolve, reject) => {
        const task = uni.uploadFile({
          url: apiUrl,
          filePath: filePath,
          name: 'file',
          fileType: 'image',
          formData: { filename: fileName, hash: hashHex },
          header: { 'Content-Type': contentType },
          success: (uploadRes) => {
            if (uploadRes.statusCode === 200) { resolve(true); }
            else { reject(new Error(`上传失败，状态码: ${uploadRes.statusCode}`)); }
          },
          fail: (err) => { reject(new Error(`上传失败: ${err.errMsg}`)); }
        });
        task.onProgressUpdate(res => { updateStatus(`上传中 ${res.progress}%`); });
      });
      return true;
    }
  } catch (err) {
    handleError(err, '上传失败', '上传失败: ' + err.message);
    throw err;
  }
}

// 仅负责获取分析原始数据（不含进度条收尾）
async function fetchAnalysisResult(fileName) {
  const analysisUrl = `${API_BASE}/analysis/${fileName}`;
  const res = await uni.request({ url: analysisUrl, method: 'GET', timeout: 60000 });
  if (res.statusCode === 200 && res.data) return res.data;
  return { error: true, status: res.statusCode };
}

// 统一的分析处理：更新进度 / 结果计算 / 校验
async function processAnalysis(fileName, kind = 'current') {
  try {
    updateStatus('分析中...');
    showToast('分析中...');
    const raw = await fetchAnalysisResult(fileName);
    if (raw && !raw.error) {
      const { resultRef } = getReportRefs(kind);
      calculateAnalysisResults(raw, resultRef);
      validateDateOrder(true);
      if (kind === 'previous') { analysisProgressPrev.value = 99; setTimeout(() => stopProgress('previous'), 300); }
      else { analysisProgressCurrent.value = 99; setTimeout(() => stopProgress('current'), 300); }
      updateStatus('分析完成');
      showToast('分析完成');
      return true;
    } else {
      const status = raw.status;
      uni.showModal({
        title: '分析失败',
        content: `状态码: ${status}，请稍后重试。（最近GPT5不稳定，多尝试几次）`,
        showCancel: false,
        confirmText: '知道了'
      });
      return false;
    }
  } catch (err) {
    handleError(err, '获取分析结果失败', '分析失败: ' + err.message);
    throw err;
  }
}

// (旧) getAnalysisResultUnified 已被拆分为 fetchAnalysisResult + processAnalysis
// async function getAnalysisResultUnified(...) { /* replaced */ }

// 分析结果计算
async function calculateAnalysisResults(result, refs) {
  refs.value = result;
  // 计算孕周，处理胚芽长为空字符串的情况，将其转换为0
  const GS = parseInt(result["孕囊大小"] || "0");
  const CRL = parseInt(result["胚芽长"] || "0");
  const CRL_cm = CRL / 10; // 转换为厘米
  let GA0, GA1, GA2, GA3, GA4;
  if (GS !== undefined && GS !== 0) GA0 = (0.882 * GS + 33.117) / 7;    // 0. 孕囊估算（适用于5-6周前的早期评估）
  if (CRL !== undefined && CRL !== 0) {
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

// ============= 新实现：使用 Date 计算，显示时再格式化（YYYY-MM-DD） =============
function parseYMD(str) {
  if (!str) return null;
  const d = new Date(str);
  return isNaN(d.getTime()) ? null : d;
}
function addDays(date, days) {
  // 支持小数天，保留原有时分秒与毫秒，通过毫秒偏移实现精确计算
  if (!(date instanceof Date)) return null;
  return new Date(date.getTime() + days * 86400000); // 86400000 = 24*60*60*1000
}
function formatYMD(date) {
  try {
    if (!date) return '-';
    if (!(date instanceof Date)) { const d = parseYMD(date); if (!d) return '-'; date = d; }
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d2 = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d2}`;
  } catch { return '-'; }
}
function calculatelastMenstrualPeriod(examDateStr, gestationalWeeks) {
  if (!examDateStr || !gestationalWeeks || gestationalWeeks === '-') return null;
  const examDate = parseYMD(examDateStr);
  if (!examDate) return null;
  const weeks = parseFloat(gestationalWeeks);
  if (isNaN(weeks)) return null;
  return addDays(examDate, -weeks * 7); // 不取整，保留小数天，后续 addDays 转为精确毫秒
}
function calculateMiscarryDate(lastMenstrualPeriodDate, currentGestationalWeeks) {
  if (!(lastMenstrualPeriodDate instanceof Date) || !currentGestationalWeeks || currentGestationalWeeks === '-') return null;
  const weeks = parseFloat(currentGestationalWeeks);
  if (isNaN(weeks)) return null;
  return addDays(lastMenstrualPeriodDate, weeks * 7); // 同上，保留精度
}
function calculateNaturalMiscarryDate(miscarryDate) {
  if (!(miscarryDate instanceof Date)) return null;
  return addDays(miscarryDate, 23);
}
// =======================================================================

function showNaturalMiscarryModal() {
  try {
    const miscarryDate = miscarryAnalysis.value && miscarryAnalysis.value.miscarryDate;
    if (!(miscarryDate instanceof Date)) {
      showToast('请在下方选择停育前报告');
      return;
    }
    if (!prevAnalysisResult.value['日期']) {
      showToast('「超声检查日期（停育前）」未识别到，请手动输入');
      return;
    }

    const d15 = addDays(miscarryDate, 15);
    const d23 = addDays(miscarryDate, 23);
    const d32 = addDays(miscarryDate, 32);

    naturalData.value = [
      { label: `${formatYMD(d15)} 前发动`, value: '🟩🟨🟨🟨 25%' },
      { label: `${formatYMD(d23)} 前发动`, value: '🟩🟩🟨🟨 50%' },
      { label: `${formatYMD(d32)} 前发动`, value: '🟩🟩🟩🟨 75%' }
    ];

    naturalPopup.value && naturalPopup.value.open();
  } catch (err) {
    console.error('显示预自然流产概率弹窗失败:', err);
  }
}

// 自定义弹窗：状态与引用
const naturalPopup = ref(null);
const naturalData = ref([]);

function closeNaturalPopup() {
  try { naturalPopup.value && naturalPopup.value.close(); } catch (e) { /* noop */ }
}

// 原 addDaysYMD 已弃用，不再使用。

async function executeTest(testType) {
  const testConfig = {
    'normal': {
      imageUrl: `${API_BASE}/images/B08.jpg`,
      apiUrl: `${API_BASE}/analysis/test`,
      resultRef: analysisResult,
      imageRef: imageUrl
    },
    'miscarry': {
      imageUrl: `${API_BASE}/images/B02.jpg`,
      apiUrl: `${API_BASE}/analysis/test2`,
      resultRef: analysisResult,
      imageRef: imageUrl
    },
    'previous': {
      imageUrl: `${API_BASE}/images/B01.jpg`,
      apiUrl: `${API_BASE}/analysis/test4`,
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
    const res = await uni.request({ url: config.apiUrl, method: 'GET', timeout: 30000 });
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

// 进度条相关
const analysisProgressCurrent = ref(0);
const analysisProgressPrev = ref(0);
let progressTimerCurrent = null;
let progressTimerPrev = null;

function startProgress(kind) {
  const isPrev = kind === 'previous';
  stopProgress(kind);
  if (isPrev) {
    analysisProgressPrev.value = 0;
    progressTimerPrev = setInterval(() => {
      if (analysisProgressPrev.value < 99) {
        analysisProgressPrev.value = Math.min(99, analysisProgressPrev.value + 3);
      }
    }, 1000);
  } else {
    analysisProgressCurrent.value = 0;
    progressTimerCurrent = setInterval(() => {
      if (analysisProgressCurrent.value < 99) {
        analysisProgressCurrent.value = Math.min(99, analysisProgressCurrent.value + 3);
      }
    }, 1000);
  }
}

function stopProgress(kind) {
  const isPrev = kind === 'previous';
  if (isPrev) {
    if (progressTimerPrev) { clearInterval(progressTimerPrev); progressTimerPrev = null; }
    analysisProgressPrev.value = 0;
  } else {
    if (progressTimerCurrent) { clearInterval(progressTimerCurrent); progressTimerCurrent = null; }
    analysisProgressCurrent.value = 0;
  }
}

function arrayBufferToHex(ab) {
  return [...new Uint8Array(ab)].map(b => b.toString(16).padStart(2, '0')).join('');
}
async function computeImageHashHex(filePath, fileObj) {
  try {
    updateStatus('正在计算哈希...');
    let arrayBuffer;
    if (fileObj && typeof File !== 'undefined' && fileObj instanceof File) {
      arrayBuffer = await fileObj.arrayBuffer();
    } else {
      const fs = uni.getFileSystemManager && uni.getFileSystemManager();
      if (!fs) { throw new Error('当前平台不支持文件系统读取'); }
      arrayBuffer = await new Promise((resolve, reject) => {
        fs.readFile({ filePath, success: res => resolve(res.data), fail: err => reject(err) });
      });
    }
    if (crypto && crypto.subtle) {
      const digest = await crypto.subtle.digest('SHA-256', arrayBuffer);
      return arrayBufferToHex(digest);
    } else {
      let hash = 0; const view = new Uint8Array(arrayBuffer);
      for (let i = 0; i < view.length; i++) { hash = (hash * 31 + view[i]) >>> 0; }
      return hash.toString(16).padStart(8, '0');
    }
  } catch (e) {
    console.warn('计算哈希失败，继续上传:', e);
    return null;
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
}

/* 主体内容卡片 */
.content-card {
  width: 100%;
  max-width: 650rpx;
  background-color: #fff;
  border-radius: 24rpx;
  padding: 40rpx 30rpx;
  /* 内边距 */
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 30rpx;
  /* 模块间距 */
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
  background: linear-gradient(45deg, #66e0c6, #37a898);
  /* 渊变色按钮，更具活力 */
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

.upload-btn::after {
  border: none;
}

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
  background-color: #f0f0f0;
  /* 图片加载前的背景色 */
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
.comparison-data {
  gap: 12rpx;
}

/* 区域内列表（原 result-list 与 single-report-data 公共部分） */
.result-list,
.single-report-data {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

/* single-report-data 原有的额外外边距 */
.single-report-data {
  margin-bottom: 24rpx;
}

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
.result-item {
  justify-content: space-between;
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

/* 自定义弹窗样式 */
.custom-dialog {
  width: 600rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx 30rpx;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  margin-top: 20rpx;
}

.dialog-btn {
  background: linear-gradient(45deg, #66e0c6, #37a898);
  color: #fff;
  box-shadow: 0 4rpx 12rpx rgba(55, 168, 152, 0.3);
  transition: all 0.2s ease-in-out;
}

/* 文件选择器样式 */
:deep(.file-picker__box) {
  /* width: 168rpx !important; */
  width: 100% !important;
  height: 150rpx !important;
  border-radius: 16rpx !important;
  padding-top: 0;
  /* .file-picker__progress {
		display: none;
	}	 */
}

:deep(.file-picker__box-content) {
  border-radius: 16rpx !important;
  border: none !important;
}

.progress-mode {
  width: 100%;
}

.progress-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  flex: 1;
}

.progress-text {
  font-size: 24rpx;
  font-weight: 600;
}

.progress-bar {
  width: 100%;
  height: 14rpx;
  background: rgba(255, 255, 255, 0.35);
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-bar-inner {
  height: 100%;
  background: #ffffff;
  width: 0%;
  transition: width 0.8s ease;
  border-radius: 8rpx;
}

/* 停育前按钮进度可复用同样样式，如需区分可根据 .prev-btn .progress-bar-inner 自定义颜色 */
.prev-btn .progress-bar-inner {
  background: #4a4e91;
}

/* 页脚样式 */
.page-footer {
  width: 100%;
  max-width: 650rpx;
  padding: 40rpx 30rpx 80rpx;
  box-sizing: border-box;
  text-align: center;
  color: #8a9399;
  font-size: 22rpx;
  line-height: 1.6;
}

.page-footer .meta {
  display: block;
  margin-top: 12rpx;
  font-size: 20rpx;
  color: #b0b7bc;
}

.footer-link {
  color: #66e0c6;
  text-decoration: underline;
  font-weight: 600;
  cursor: pointer;
}
</style>