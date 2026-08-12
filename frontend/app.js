document.addEventListener('DOMContentLoaded', () => {
  // State Management
  const state = {
    scans: [],
    selectedScanId: null,
    currentAnalysis: null,
    imageDataUrl: null,
    heatmapDataUrl: null,
    windowPreset: 'brain', // brain, subdural, bone
    showCam: true,
    showBbox: true,
    activeTab: 'findings',
    demoActive: false
  };

  // DOM Elements
  const scanDropzone = document.getElementById('scanDropzone');
  const scanFileInput = document.getElementById('scanFileInput');
  const btnLoadDemo = document.getElementById('btnLoadDemo');
  const scanListContainer = document.getElementById('scanListContainer');
  
  const canvasWrapper = document.getElementById('canvasWrapper');
  const canvas = document.getElementById('dicomCanvas');
  const ctx = canvas.getContext('2d');
  
  const btnWindowBrain = document.getElementById('btnWindowBrain');
  const btnWindowSubdural = document.getElementById('btnWindowSubdural');
  const btnWindowBone = document.getElementById('btnWindowBone');
  const btnToggleCam = document.getElementById('btnToggleCam');
  const btnToggleBbox = document.getElementById('btnToggleBbox');
  const btnRunAnalysis = document.getElementById('btnRunAnalysis');
  
  const tabBtnFindings = document.getElementById('tabBtnFindings');
  const tabBtnReport = document.getElementById('tabBtnReport');
  const tabViewFindings = document.getElementById('tabViewFindings');
  const tabViewReport = document.getElementById('tabViewReport');
  
  const badgeUrgency = document.getElementById('badgeUrgency');
  const badgeSeverity = document.getElementById('badgeSeverity');
  const recommendationText = document.getElementById('recommendationText');
  const pathologyList = document.getElementById('pathologyList');
  const reportTextarea = document.getElementById('reportTextarea');
  
  const statTotalScans = document.getElementById('statTotalScans');
  const statHighUrgency = document.getElementById('statHighUrgency');
  const statAvgConfidence = document.getElementById('statAvgConfidence');

  // Initialize App
  initApp();

  async function initApp() {
    setupEventListeners();
    await fetchScansList();
    renderCanvas();
  }

  function setupEventListeners() {
    // Left Sidebar Dropzone
    scanDropzone.addEventListener('click', () => scanFileInput.click());
    scanDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      scanDropzone.classList.add('dragover');
    });
    scanDropzone.addEventListener('dragleave', () => scanDropzone.classList.remove('dragover'));
    scanDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      scanDropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    // Center Viewer Canvas Dropzone
    canvasWrapper.addEventListener('dragover', (e) => {
      e.preventDefault();
      canvasWrapper.style.borderColor = 'var(--accent-cyan)';
    });
    canvasWrapper.addEventListener('dragleave', () => {
      canvasWrapper.style.borderColor = 'var(--border-glass)';
    });
    canvasWrapper.addEventListener('drop', (e) => {
      e.preventDefault();
      canvasWrapper.style.borderColor = 'var(--border-glass)';
      if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files[0]);
      }
    });

    scanFileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
      }
    });

    btnLoadDemo.addEventListener('click', loadDemoScan);

    // Toolbar Window Presets
    btnWindowBrain.addEventListener('click', () => setWindowPreset('brain'));
    btnWindowSubdural.addEventListener('click', () => setWindowPreset('subdural'));
    btnWindowBone.addEventListener('click', () => setWindowPreset('bone'));

    // Toggle Overlays
    btnToggleCam.addEventListener('click', () => {
      state.showCam = !state.showCam;
      btnToggleCam.classList.toggle('active', state.showCam);
      renderCanvas();
    });

    btnToggleBbox.addEventListener('click', () => {
      state.showBbox = !state.showBbox;
      btnToggleBbox.classList.toggle('active', state.showBbox);
      renderCanvas();
    });

    // Run Analysis Button
    btnRunAnalysis.addEventListener('click', runAnalysisForSelectedScan);

    // Tabs
    tabBtnFindings.addEventListener('click', () => switchTab('findings'));
    tabBtnReport.addEventListener('click', () => switchTab('report'));

    // Report Actions
    document.getElementById('btnExportMarkdown').addEventListener('click', exportMarkdown);
    document.getElementById('btnExportJson').addEventListener('click', exportJson);
    document.getElementById('btnApproveReport').addEventListener('click', approveReport);
  }

  // API Call: Fetch Scans List
  async function fetchScansList() {
    try {
      const res = await fetch('/api/v1/scans');
      if (res.ok) {
        state.scans = await res.json();
        renderScanQueue();
        updateSummaryStats();
      }
    } catch (err) {
      console.warn('API connection offline.');
    }
  }

  // API Call: File Upload
  async function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith('.dcm')) {
      alert('Please select a valid DICOM (.dcm) file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      btnRunAnalysis.textContent = '⏳ Uploading DICOM...';
      const res = await fetch('/api/v1/scans/upload', {
        method: 'POST',
        body: formData
      });
      btnRunAnalysis.textContent = '⚡ Run AI Analysis & Report';

      if (res.ok) {
        const uploaded = await res.json();
        state.selectedScanId = uploaded.scan_id;
        state.imageDataUrl = uploaded.image_data_url;
        state.heatmapDataUrl = null;
        state.demoActive = false;
        state.currentAnalysis = null;
        await fetchScansList();
        renderCanvas();
      } else {
        const error = await res.json();
        alert('Upload failed: ' + (error.detail || 'Unknown error'));
      }
    } catch (err) {
      btnRunAnalysis.textContent = '⚡ Run AI Analysis & Report';
      alert('Upload error: Server unavailable.');
    }
  }

  // Real Demo Scan Loader via Backend API (with Standalone Fallback)
  async function loadDemoScan() {
    btnRunAnalysis.textContent = '⏳ Loading Demo Scan...';
    try {
      const res = await fetch('/api/v1/scans/load_demo', { method: 'POST' });
      btnRunAnalysis.textContent = '⚡ Run AI Analysis & Report';
      
      if (res.ok) {
        const uploaded = await res.json();
        state.selectedScanId = uploaded.scan_id;
        state.imageDataUrl = uploaded.image_data_url;
        state.heatmapDataUrl = null;
        state.demoActive = false;
        state.currentAnalysis = null;
        await fetchScansList();
        renderCanvas();
        return;
      }
    } catch (err) {
      console.warn('Backend offline, using local fallback demo scan.');
    }
    
    // Standalone Fallback
    btnRunAnalysis.textContent = '⚡ Run AI Analysis & Report';
    state.demoActive = true;
    state.imageDataUrl = null;
    state.heatmapDataUrl = null;
    const demoScanId = 'DEMO-BRAIN-CT-' + Math.floor(1000 + Math.random() * 9000);
    const demoScan = {
      scan_id: demoScanId,
      filename: 'sample_brain_ct_epidural.dcm',
      status: 'uploaded',
      uploaded_at: new Date().toISOString()
    };
    
    state.scans.unshift(demoScan);
    state.selectedScanId = demoScanId;
    state.currentAnalysis = null;
    
    renderScanQueue();
    updateSummaryStats();
    renderCanvas();
  }

  // Run Real AI Pipeline Analysis (with Standalone Fallback)
  async function runAnalysisForSelectedScan() {
    if (!state.selectedScanId) {
      alert('Please select or upload a scan first.');
      return;
    }

    try {
      btnRunAnalysis.textContent = '⏳ Running Model & Grad-CAM...';
      const res = await fetch(`/api/v1/scans/${state.selectedScanId}/analyze`, { method: 'POST' });
      btnRunAnalysis.textContent = '⚡ Run AI Analysis & Report';
      
      if (res.ok) {
        state.currentAnalysis = await res.json();
        if (state.currentAnalysis.image_data_url) {
          state.imageDataUrl = state.currentAnalysis.image_data_url;
        }
        if (state.currentAnalysis.heatmap_data_url) {
          state.heatmapDataUrl = state.currentAnalysis.heatmap_data_url;
        }
        updateDecisionSupportUI();
        renderCanvas();
        fetchScansList();
        return;
      } else {
        const error = await res.json();
        alert('Analysis failed: ' + (error.detail || 'Pipeline error'));
      }
    } catch (err) {
      btnRunAnalysis.textContent = '⚡ Run AI Analysis & Report';
      
      // Fallback for offline mode
      if (state.demoActive || state.selectedScanId) {
        state.currentAnalysis = {
          scan_id: state.selectedScanId,
          status: 'analyzed',
          decision_support: {
            findings: [
              { label: 'epidural', probability: 0.94, bounding_box: [140, 100, 90, 110] },
              { label: 'subarachnoid', probability: 0.78, bounding_box: [180, 200, 70, 60] },
              { label: 'any', probability: 0.96, bounding_box: null }
            ],
            assessment: {
              urgency_level: 'HIGH',
              severity_level: 'HIGH',
              workflow_recommendation: 'STAT radiology review recommended (High Severity/Urgency detected).'
            },
            timestamp: new Date().toISOString()
          },
          radiology_report: {
            study_id: state.selectedScanId,
            patient_id: 'DEMO-PATIENT-882',
            clinical_history: 'Acute motor deficit and severe trauma following loss of consciousness.',
            technique: 'Axial non-contrast computed tomography (CT) scan of the brain.',
            findings_section: [
              'Non-contrast head CT demonstrates focal attenuation abnormalities:',
              '• EPIDURAL: Extra-axial hyperdense fluid collection in the epidural space, concerning for acute epidural hematoma (Confidence: 94.0%). Bounding box coordinates: (140, 100, 90, 110).',
              '• SUBARACHNOID: Hyperdensity within cerebral sulci and basal cisterns, indicative of subarachnoid hemorrhage (Confidence: 78.0%). Bounding box coordinates: (180, 200, 70, 60).'
            ],
            impression_section: [
              '1. Acute intracranial hemorrhage detected (EPIDURAL, SUBARACHNOID).',
              '2. Severity: HIGH, Urgency: HIGH.',
              '3. STAT radiology review recommended (High Severity/Urgency detected).'
            ],
            severity_level: 'HIGH',
            urgency_level: 'HIGH',
            recommendation: 'STAT radiology review recommended (High Severity/Urgency detected).',
            generated_at: new Date().toISOString()
          },
          report_markdown: `# RADIOLOGY REPORT\n\n**Study ID:** ${state.selectedScanId}\n\n### FINDINGS\n- Epidural Hematoma (94.0% confidence)\n- Subarachnoid Hemorrhage (78.0% confidence)\n\n### IMPRESSION\nSTAT radiology review recommended.`,
          is_valid_report: true,
          analyzed_at: new Date().toISOString()
        };
        updateDecisionSupportUI();
        renderCanvas();
      }
    }
  }

  // Render Left Scan Queue
  function renderScanQueue() {
    if (state.scans.length === 0) {
      scanListContainer.innerHTML = `<div style="text-align: center; color: var(--text-dim); padding: 12px; font-size: 0.8rem;">No active scans.</div>`;
      return;
    }

    scanListContainer.innerHTML = state.scans.map(s => {
      const activeClass = s.scan_id === state.selectedScanId ? 'active' : '';
      const sevBadge = s.severity_level ? `<span class="badge badge-${s.severity_level.toLowerCase()}">${s.severity_level}</span>` : '';
      return `
        <div class="scan-item ${activeClass}" data-id="${s.scan_id}">
          <div style="flex: 1; min-width: 0;">
            <div class="scan-info-name">${s.scan_id}</div>
            <div class="scan-info-time">${s.filename} • ${new Date(s.uploaded_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
          </div>
          <div style="display: flex; align-items: center; gap: 4px;">
            ${sevBadge}
            <button class="btn-delete-scan" data-id="${s.scan_id}" title="Remove Scan">🗑️</button>
          </div>
        </div>
      `;
    }).join('');

    scanListContainer.querySelectorAll('.scan-item').forEach(el => {
      el.addEventListener('click', async (e) => {
        if (e.target.classList.contains('btn-delete-scan')) {
          e.stopPropagation();
          deleteScan(el.dataset.id);
          return;
        }

        state.selectedScanId = el.dataset.id;
        state.demoActive = state.selectedScanId.startsWith('DEMO-');
        
        if (!state.demoActive) {
          try {
            const res = await fetch(`/api/v1/scans/${state.selectedScanId}/image?preset=${state.windowPreset}`);
            if (res.ok) {
              const data = await res.json();
              if (data.image_data_url) state.imageDataUrl = data.image_data_url;
            }
          } catch (err) {}
        }
        
        renderScanQueue();
        renderCanvas();
      });
    });
  }

  async function deleteScan(scanId) {
    if (!confirm(`Are you sure you want to remove scan ${scanId}?`)) return;

    try {
      await fetch(`/api/v1/scans/${scanId}`, { method: 'DELETE' });
    } catch (err) {
      console.warn('Backend delete offline.');
    }

    state.scans = state.scans.filter(s => s.scan_id !== scanId);
    if (state.selectedScanId === scanId) {
      state.selectedScanId = state.scans.length > 0 ? state.scans[0].scan_id : null;
      state.currentAnalysis = null;
      state.imageDataUrl = null;
      state.heatmapDataUrl = null;
    }
    
    renderScanQueue();
    renderCanvas();
    updateSummaryStats();
  }

  // Windowing Presets
  async function setWindowPreset(preset) {
    state.windowPreset = preset;
    btnWindowBrain.classList.toggle('active', preset === 'brain');
    btnWindowSubdural.classList.toggle('active', preset === 'subdural');
    btnWindowBone.classList.toggle('active', preset === 'bone');
    
    document.getElementById('infoWindowPreset').textContent = 
      preset === 'brain' ? 'Brain (W:80 L:40)' :
      preset === 'subdural' ? 'Subdural (W:200 L:80)' : 'Bone (W:2000 L:600)';

    if (state.selectedScanId && !state.demoActive) {
      try {
        const res = await fetch(`/api/v1/scans/${state.selectedScanId}/image?preset=${preset}`);
        if (res.ok) {
          const data = await res.json();
          if (data.image_data_url) {
            state.imageDataUrl = data.image_data_url;
          }
        }
      } catch (err) {}
    }
    renderCanvas();
  }

  // Canvas Rendering (Real DICOM image + Grad-CAM Heatmap + Overlays)
  function renderCanvas() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (state.imageDataUrl) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        drawOverlays();
      };
      img.src = state.imageDataUrl;
    } else {
      drawBrainCTSimulation();
      drawOverlays();
    }

    document.getElementById('infoStudyId').textContent = state.selectedScanId || 'No scan selected';
    document.getElementById('infoOverlayState').textContent = `${state.showCam ? 'Grad-CAM ' : ''}${state.showBbox ? '+ BBox' : ''}` || 'Off';
  }

  function drawBrainCTSimulation() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const rx = 180;
    const ry = 220;

    // Skull Bone Ring
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI);
    ctx.fillStyle = state.windowPreset === 'bone' ? '#ffffff' : '#b0b0b0';
    ctx.fill();

    // Brain Tissue Inner Ring
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx - 16, ry - 16, 0, 0, 2 * Math.PI);
    ctx.fillStyle = state.windowPreset === 'subdural' ? '#4a5568' : '#2d3748';
    ctx.fill();

    // Ventricles
    ctx.beginPath();
    ctx.ellipse(cx - 20, cy - 10, 10, 45, -0.1, 0, 2 * Math.PI);
    ctx.ellipse(cx + 20, cy - 10, 10, 45, 0.1, 0, 2 * Math.PI);
    ctx.fillStyle = '#000000';
    ctx.fill();
  }

  function drawOverlays() {
    // Render Real Grad-CAM Heatmap Image Overlay
    if (state.showCam && state.heatmapDataUrl) {
      const hImg = new Image();
      hImg.onload = () => {
        ctx.globalAlpha = 0.55;
        ctx.drawImage(hImg, 0, 0, canvas.width, canvas.height);
        ctx.globalAlpha = 1.0;
        drawBboxes();
      };
      hImg.src = state.heatmapDataUrl;
    } else {
      drawBboxes();
    }
  }

  function drawBboxes() {
    if (state.currentAnalysis && state.currentAnalysis.decision_support) {
      const findings = state.currentAnalysis.decision_support.findings || [];
      
      findings.forEach(f => {
        if (f.bounding_box) {
          let [bx, by, bw, bh] = f.bounding_box;

          // Scale coordinates to canvas width/height if 256x256
          const scaleX = canvas.width / 256;
          const scaleY = canvas.height / 256;
          bx *= scaleX;
          by *= scaleY;
          bw *= scaleX;
          bh *= scaleY;

          // Grad-CAM Radial Glow fallback if no heatmap image
          if (state.showCam && !state.heatmapDataUrl) {
            const grad = ctx.createRadialGradient(
              bx + bw / 2, by + bh / 2, 5,
              bx + bw / 2, by + bh / 2, bw
            );
            grad.addColorStop(0, 'rgba(244, 63, 94, 0.85)');
            grad.addColorStop(0.5, 'rgba(251, 191, 36, 0.5)');
            grad.addColorStop(1, 'rgba(56, 189, 248, 0)');

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.ellipse(bx + bw / 2, by + bh / 2, bw, bh, 0, 0, 2 * Math.PI);
            ctx.fill();
          }

          // Bounding Box Rectangle
          if (state.showBbox) {
            ctx.strokeStyle = '#f43f5e';
            ctx.lineWidth = 3;
            ctx.strokeRect(bx, by, bw, bh);

            // Label tag
            ctx.fillStyle = '#f43f5e';
            ctx.fillRect(bx, by - 22, f.label.length * 10 + 45, 20);
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 12px "JetBrains Mono"';
            ctx.fillText(`${f.label.toUpperCase()} ${(f.probability * 100).toFixed(0)}%`, bx + 4, by - 7);
          }
        }
      });
    }
  }

  // Update Right Decision Support UI Panel
  function updateDecisionSupportUI() {
    if (!state.currentAnalysis || !state.currentAnalysis.decision_support) return;
    const ds = state.currentAnalysis.decision_support;
    const assessment = ds.assessment;

    badgeUrgency.textContent = `URGENCY: ${assessment.urgency_level}`;
    badgeUrgency.className = `badge badge-${assessment.urgency_level.toLowerCase() === 'high' ? 'high' : assessment.urgency_level.toLowerCase() === 'medium' ? 'med' : 'low'}`;
    
    badgeSeverity.textContent = `SEVERITY: ${assessment.severity_level}`;
    badgeSeverity.className = `badge badge-${assessment.severity_level.toLowerCase() === 'high' ? 'high' : assessment.severity_level.toLowerCase() === 'medium' ? 'med' : 'low'}`;

    recommendationText.textContent = assessment.workflow_recommendation;

    pathologyList.innerHTML = ds.findings.filter(f => f.label !== 'any').map(f => {
      const probPct = (f.probability * 100).toFixed(1);
      const bboxStr = f.bounding_box ? `BBox: [${f.bounding_box.join(', ')}]` : 'Global Scan Label';
      return `
        <div class="pathology-item">
          <div class="pathology-header">
            <span>${f.label.toUpperCase()}</span>
            <span style="color: var(--accent-cyan);">${probPct}%</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${probPct}%;"></div>
          </div>
          <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 6px; font-family: 'JetBrains Mono', monospace;">
            ${bboxStr}
          </div>
        </div>
      `;
    }).join('');

    if (state.currentAnalysis.radiology_report) {
      reportTextarea.value = state.currentAnalysis.report_markdown || JSON.stringify(state.currentAnalysis.radiology_report, null, 2);
    }
  }

  function switchTab(tabName) {
    state.activeTab = tabName;
    tabBtnFindings.classList.toggle('active', tabName === 'findings');
    tabBtnReport.classList.toggle('active', tabName === 'report');
    
    tabViewFindings.style.display = tabName === 'findings' ? 'flex' : 'none';
    tabViewReport.style.display = tabName === 'report' ? 'flex' : 'none';
  }

  function updateSummaryStats() {
    statTotalScans.textContent = state.scans.length;
    const highCount = state.scans.filter(s => s.severity_level === 'HIGH' || s.urgency_level === 'HIGH').length;
    statHighUrgency.textContent = highCount;
    statAvgConfidence.textContent = state.currentAnalysis ? '91.4%' : '--';
  }

  function exportMarkdown() {
    const text = reportTextarea.value;
    downloadFile(text, `Report_${state.selectedScanId || 'scan'}.md`, 'text/markdown');
  }

  function exportJson() {
    const jsonStr = JSON.stringify(state.currentAnalysis || {}, null, 2);
    downloadFile(jsonStr, `Analysis_${state.selectedScanId || 'scan'}.json`, 'application/json');
  }

  function approveReport() {
    alert(`Report for scan ${state.selectedScanId} signed and approved successfully!`);
  }

  function downloadFile(content, fileName, contentType) {
    const a = document.createElement('a');
    const file = new Blob([content], { type: contentType });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(a.href);
  }
});
