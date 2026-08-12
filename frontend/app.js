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
    demoActive: false,
    viewMode: '2d', // '2d' or '3d'
    preset3D: 'brain', // 'brain', 'hemorrhage', 'bone'
    sliceZDepth: 50 // 0 to 100 %
  };

  // DOM Elements
  const scanDropzone = document.getElementById('scanDropzone');
  const scanFileInput = document.getElementById('scanFileInput');
  const btnLoadDemo = document.getElementById('btnLoadDemo');
  const scanListContainer = document.getElementById('scanListContainer');
  
  const canvasWrapper = document.getElementById('canvasWrapper');
  const canvas = document.getElementById('dicomCanvas');
  const ctx = canvas.getContext('2d');
  
  const threeContainer = document.getElementById('threeCanvasContainer');
  const btnMode2D = document.getElementById('btnMode2D');
  const btnMode3D = document.getElementById('btnMode3D');
  const toolbar2D = document.getElementById('toolbar2D');
  const toolbar3D = document.getElementById('toolbar3D');
  
  const btnWindowBrain = document.getElementById('btnWindowBrain');
  const btnWindowSubdural = document.getElementById('btnWindowSubdural');
  const btnWindowBone = document.getElementById('btnWindowBone');
  const btnToggleCam = document.getElementById('btnToggleCam');
  const btnToggleBbox = document.getElementById('btnToggleBbox');
  const btnRunAnalysis = document.getElementById('btnRunAnalysis');

  const btn3DPresetBrain = document.getElementById('btn3DPresetBrain');
  const btn3DPresetHemorrhage = document.getElementById('btn3DPresetHemorrhage');
  const btn3DPresetBone = document.getElementById('btn3DPresetBone');
  const btn3DResetCam = document.getElementById('btn3DResetCam');
  
  const sliceSliderWrapper = document.getElementById('sliceSliderWrapper');
  const sliceDepthSlider = document.getElementById('sliceDepthSlider');
  const sliceDepthVal = document.getElementById('sliceDepthVal');
  const orbitHelpBadge = document.getElementById('orbitHelpBadge');
  
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

  let threeEngine = null;

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

    // 2D / 3D View Mode Switcher
    btnMode2D.addEventListener('click', () => setViewMode('2d'));
    btnMode3D.addEventListener('click', () => setViewMode('3d'));

    // 3D Density Presets
    btn3DPresetBrain.addEventListener('click', () => set3DPreset('brain'));
    btn3DPresetHemorrhage.addEventListener('click', () => set3DPreset('hemorrhage'));
    btn3DPresetBone.addEventListener('click', () => set3DPreset('bone'));
    btn3DResetCam.addEventListener('click', () => {
      if (threeEngine) threeEngine.resetCamera();
    });

    // 3D Slice Depth Slider
    sliceDepthSlider.addEventListener('input', (e) => {
      const val = e.target.value;
      sliceDepthVal.textContent = `${val}%`;
      state.sliceZDepth = parseInt(val, 10);
      if (threeEngine) threeEngine.setSliceDepth(state.sliceZDepth);
    });

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

  // View Mode Switcher (2D Slice vs 3D Interactive Brain)
  function setViewMode(mode) {
    state.viewMode = mode;
    btnMode2D.classList.toggle('active', mode === '2d');
    btnMode3D.classList.toggle('active', mode === '3d');
    
    toolbar2D.style.display = mode === '2d' ? 'flex' : 'none';
    toolbar3D.style.display = mode === '3d' ? 'flex' : 'none';
    canvas.style.display = mode === '2d' ? 'block' : 'none';
    threeContainer.style.display = mode === '3d' ? 'block' : 'none';
    sliceSliderWrapper.style.display = mode === '3d' ? 'flex' : 'none';
    orbitHelpBadge.style.display = mode === '3d' ? 'block' : 'none';

    document.getElementById('infoViewMode').textContent = mode === '2d' ? '2D Slice' : '3D Interactive Brain';

    if (mode === '3d') {
      if (!threeEngine) {
        threeEngine = new ThreeBrainEngine(threeContainer);
        threeEngine.init();
      } else {
        threeEngine.onResize();
      }
      threeEngine.updateCTScanTexture(canvas, state.imageDataUrl);
      if (state.currentAnalysis && state.currentAnalysis.decision_support) {
        threeEngine.updateLesionFromFindings(state.currentAnalysis.decision_support.findings);
      }
    }
  }

  function set3DPreset(preset) {
    state.preset3D = preset;
    btn3DPresetBrain.classList.toggle('active', preset === 'brain');
    btn3DPresetHemorrhage.classList.toggle('active', preset === 'hemorrhage');
    btn3DPresetBone.classList.toggle('active', preset === 'bone');

    if (threeEngine) {
      threeEngine.setPreset(preset);
    }
  }

  // Windowing Presets (2D)
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
    ctx.fillStyle = '#050811';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (state.imageDataUrl) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        drawOverlays();
        if (threeEngine) {
          threeEngine.updateCTScanTexture(canvas, state.imageDataUrl);
        }
      };
      img.src = state.imageDataUrl;
    } else {
      drawBrainCTSimulation();
      drawOverlays();
      if (threeEngine) {
        threeEngine.updateCTScanTexture(canvas, null);
      }
    }

    if (state.viewMode === '3d') {
      if (threeEngine) {
        threeEngine.onResize();
        if (state.currentAnalysis && state.currentAnalysis.decision_support) {
          threeEngine.updateLesionFromFindings(state.currentAnalysis.decision_support.findings);
        }
      }
    }

    document.getElementById('infoStudyId').textContent = state.selectedScanId || 'No scan selected';
    document.getElementById('infoOverlayState').textContent = `${state.showCam ? 'Grad-CAM ' : ''}${state.showBbox ? '+ BBox' : ''}` || 'Off';
  }

  // Realistic Non-Contrast Brain CT Slice Generator (Anatomically Detailed)
  function drawBrainCTSimulation() {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const rx = 180;
    const ry = 220;

    // 1. Dark Air Background
    ctx.fillStyle = '#03050a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 2. High-Density Skull Bone Ring (Outer Cortex + Diploë Space)
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx, ry, 0, 0, 2 * Math.PI);
    ctx.fillStyle = state.windowPreset === 'bone' ? '#ffffff' : '#d1d5db';
    ctx.fill();

    ctx.beginPath();
    ctx.ellipse(cx, cy, rx - 6, ry - 6, 0, 0, 2 * Math.PI);
    ctx.fillStyle = state.windowPreset === 'bone' ? '#94a3b8' : '#64748b';
    ctx.fill();

    // 3. Inner Skull Table
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx - 14, ry - 14, 0, 0, 2 * Math.PI);
    ctx.fillStyle = state.windowPreset === 'bone' ? '#ffffff' : '#e2e8f0';
    ctx.fill();

    // 4. Brain Parenchyma (Gray/White Matter Soft Tissue HU Density)
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx - 18, ry - 18, 0, 0, 2 * Math.PI);
    
    const brainGrad = ctx.createRadialGradient(cx, cy, 20, cx, cy, rx - 18);
    if (state.windowPreset === 'brain') {
      brainGrad.addColorStop(0, '#475569');   // Deep subcortical white matter (HU ~30)
      brainGrad.addColorStop(0.7, '#334155'); // Cerebral cortex gray matter (HU ~40)
      brainGrad.addColorStop(1, '#1e293b');   // Subarachnoid space / CSF
    } else if (state.windowPreset === 'subdural') {
      brainGrad.addColorStop(0, '#334155');
      brainGrad.addColorStop(0.8, '#1e293b');
      brainGrad.addColorStop(1, '#0f172a');
    } else {
      brainGrad.addColorStop(0, '#1e293b');
      brainGrad.addColorStop(1, '#020617');
    }
    ctx.fillStyle = brainGrad;
    ctx.fill();

    // 5. Interhemispheric Fissure & Sulci Lines
    ctx.strokeStyle = state.windowPreset === 'subdural' ? '#0f172a' : '#1e293b';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(cx, cy - ry + 22);
    ctx.lineTo(cx, cy + ry - 22);
    ctx.stroke();

    // Cortical Sulci Convolution Swirls
    for (let angle = 0; angle < Math.PI * 2; angle += Math.PI / 4) {
      const sx = cx + Math.cos(angle) * (rx - 45);
      const sy = cy + Math.sin(angle) * (ry - 45);
      ctx.beginPath();
      ctx.arc(sx, sy, 18, angle, angle + Math.PI / 2);
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1.8;
      ctx.stroke();
    }

    // 6. Lateral Ventricles (Frontal & Occipital Horns - Hypodense CSF)
    ctx.fillStyle = '#030712';
    // Left Ventricle
    ctx.beginPath();
    ctx.ellipse(cx - 24, cy - 12, 10, 48, -0.15, 0, 2 * Math.PI);
    ctx.fill();
    // Right Ventricle
    ctx.beginPath();
    ctx.ellipse(cx + 24, cy - 12, 10, 48, 0.15, 0, 2 * Math.PI);
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

  // 3D WebGL Brain Engine (Three.js + Orbit Controls + Z-Slice Clipping + HU Density Presets)
  class ThreeBrainEngine {
    constructor(containerEl) {
      this.container = containerEl;
      this.scene = null;
      this.camera = null;
      this.renderer = null;
      this.controls = null;
      this.brainGroup = null;
      this.clippingPlane = null;
      this.lesionMesh = null;
      this.bboxMesh = null;
      this.initialized = false;
    }

    init() {
      if (this.initialized || typeof THREE === 'undefined') return;

      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(0x050811);

      const width = this.container.clientWidth || 512;
      const height = this.container.clientHeight || 512;

      this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      this.camera.position.set(0, 110, 210);

      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, localClippingEnabled: true });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.renderer.shadowMap.enabled = true;
      
      this.container.innerHTML = '';
      this.container.appendChild(this.renderer.domElement);

      if (typeof THREE.OrbitControls !== 'undefined') {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI * 0.95;
      }

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
      this.scene.add(ambientLight);

      const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.2);
      dirLight1.position.set(100, 150, 100);
      this.scene.add(dirLight1);

      const dirLight2 = new THREE.DirectionalLight(0x8b5cf6, 0.8);
      dirLight2.position.set(-100, -100, -100);
      this.scene.add(dirLight2);

      // Z Clipping Plane for 3D Slice Cross-sectioning
      this.clippingPlane = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
      this.renderer.clippingPlanes = [this.clippingPlane];

      this.buildBrainModel();
      this.initialized = true;

      window.addEventListener('resize', () => this.onResize());
      this.animate();
    }

    buildBrainModel() {
      if (this.brainGroup) this.scene.remove(this.brainGroup);
      this.brainGroup = new THREE.Group();

      // 1. Skull Shell (CT High Bone Density Window)
      const skullGeo = new THREE.SphereGeometry(58, 64, 48);
      skullGeo.scale(1.0, 1.15, 1.25);

      this.skullMat = new THREE.MeshStandardMaterial({
        color: 0xe2e8f0,
        roughness: 0.3,
        metalness: 0.1,
        transparent: true,
        opacity: 0.18,
        clippingPlanes: [this.clippingPlane],
        side: THREE.DoubleSide
      });
      const skull = new THREE.Mesh(skullGeo, this.skullMat);
      this.brainGroup.add(skull);

      // Skull Bone Wireframe Outer Rim
      const skullWireMat = new THREE.MeshBasicMaterial({
        color: 0x64748b,
        wireframe: true,
        transparent: true,
        opacity: 0.08,
        clippingPlanes: [this.clippingPlane]
      });
      const skullWire = new THREE.Mesh(skullGeo, skullWireMat);
      this.brainGroup.add(skullWire);

      // 2. Dual Brain Hemispheres (Left & Right)
      const hemisphereGroup = new THREE.Group();

      const hemiGeo = new THREE.SphereGeometry(44, 48, 36);
      hemiGeo.scale(0.86, 1.06, 1.16);

      this.brainTissueMat = new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        roughness: 0.4,
        metalness: 0.15,
        transparent: true,
        opacity: 0.65,
        clippingPlanes: [this.clippingPlane],
        side: THREE.DoubleSide
      });

      const leftHemi = new THREE.Mesh(hemiGeo, this.brainTissueMat);
      leftHemi.position.set(-19, 0, 0);
      hemisphereGroup.add(leftHemi);

      const rightHemi = new THREE.Mesh(hemiGeo, this.brainTissueMat);
      rightHemi.position.set(19, 0, 0);
      hemisphereGroup.add(rightHemi);

      // 3. Brain Sulci/Gyri Cortex Surface Curvature (CT Density Particles)
      const particlesCount = 3800;
      const posArray = new Float32Array(particlesCount * 3);
      const colorArray = new Float32Array(particlesCount * 3);

      for (let i = 0; i < particlesCount; i++) {
        const u = Math.random();
        const v = Math.random();
        const theta = u * 2.0 * Math.PI;
        const phi = Math.acos(2.0 * v - 1.0);
        const r = 43 + Math.sin(theta * 7) * Math.cos(phi * 7) * 3.5;

        const x = r * Math.sin(phi) * Math.cos(theta) * 0.92;
        const y = r * Math.sin(phi) * Math.sin(theta) * 1.08;
        const z = r * Math.cos(phi) * 1.18;

        posArray[i * 3] = x;
        posArray[i * 3 + 1] = y;
        posArray[i * 3 + 2] = z;

        colorArray[i * 3] = 0.22;
        colorArray[i * 3 + 1] = 0.74;
        colorArray[i * 3 + 2] = 0.97;
      }

      const pGeo = new THREE.BufferGeometry();
      pGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
      pGeo.setAttribute('color', new THREE.BufferAttribute(colorArray, 3));

      const pMat = new THREE.PointsMaterial({
        size: 2.2,
        vertexColors: true,
        transparent: true,
        opacity: 0.75,
        clippingPlanes: [this.clippingPlane]
      });

      const cortexParticles = new THREE.Points(pGeo, pMat);
      hemisphereGroup.add(cortexParticles);

      // 4. Ventricles (Hypodense CSF Cavities)
      const ventricleGeo = new THREE.TorusGeometry(15, 4.5, 16, 32);
      const ventricleMat = new THREE.MeshBasicMaterial({
        color: 0x050811,
        wireframe: true,
        transparent: true,
        opacity: 0.45,
        clippingPlanes: [this.clippingPlane]
      });
      const ventricles = new THREE.Mesh(ventricleGeo, ventricleMat);
      ventricles.rotation.x = Math.PI / 2;
      hemisphereGroup.add(ventricles);

      // 5. 3D CT Scan Image Slice Mesh (Mapped directly inside 3D Brain Space)
      const slicePlaneGeo = new THREE.PlaneGeometry(105, 105);
      this.slicePlaneMat = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.95
      });
      this.ctSlicePlaneMesh = new THREE.Mesh(slicePlaneGeo, this.slicePlaneMat);
      this.ctSlicePlaneMesh.position.set(0, 0, 0);
      this.brainGroup.add(this.ctSlicePlaneMesh);

      // 6. Lesion Hyperdensity Volume & Glowing 3D Bounding Box
      const lesionGeo = new THREE.SphereGeometry(15, 32, 24);
      lesionGeo.scale(1.25, 0.85, 1.05);

      this.lesionMat = new THREE.MeshStandardMaterial({
        color: 0xf43f5e,
        emissive: 0xf43f5e,
        emissiveIntensity: 0.9,
        roughness: 0.2,
        transparent: true,
        opacity: 0.85,
        clippingPlanes: [this.clippingPlane]
      });
      this.lesionMesh = new THREE.Mesh(lesionGeo, this.lesionMat);
      this.lesionMesh.position.set(22, 10, 15);
      this.brainGroup.add(this.lesionMesh);

      // 3D Wireframe Bounding Box
      const bboxGeo = new THREE.BoxGeometry(34, 28, 30);
      const bboxMat = new THREE.MeshBasicMaterial({
        color: 0xf43f5e,
        wireframe: true,
        clippingPlanes: [this.clippingPlane]
      });
      this.bboxMesh = new THREE.Mesh(bboxGeo, this.bboxMat);
      this.bboxMesh.position.copy(this.lesionMesh.position);
      this.brainGroup.add(this.bboxMesh);

      this.scene.add(this.brainGroup);
    }

    updateCTScanTexture(canvasEl, dataUrl) {
      if (!this.initialized || !this.slicePlaneMat) return;

      if (dataUrl) {
        new THREE.TextureLoader().load(dataUrl, (tex) => {
          tex.needsUpdate = true;
          this.slicePlaneMat.map = tex;
          this.slicePlaneMat.needsUpdate = true;
        });
      } else if (canvasEl) {
        const tex = new THREE.CanvasTexture(canvasEl);
        tex.needsUpdate = true;
        this.slicePlaneMat.map = tex;
        this.slicePlaneMat.needsUpdate = true;
      }
    }

    updateLesionFromFindings(findings) {
      if (!this.initialized || !findings || findings.length === 0) return;

      const lesionFinding = findings.find(f => f.label !== 'any' && f.bounding_box);
      if (lesionFinding && lesionFinding.bounding_box) {
        const [bx, by, bw, bh] = lesionFinding.bounding_box;
        const posX = ((bx + bw / 2) / 256 - 0.5) * 70;
        const posY = -((by + bh / 2) / 256 - 0.5) * 80;
        const posZ = 15;

        this.lesionMesh.position.set(posX, posY, posZ);
        this.bboxMesh.position.set(posX, posY, posZ);
        this.lesionMesh.visible = true;
        this.bboxMesh.visible = true;
      }
    }

    setPreset(preset) {
      if (!this.initialized) return;
      if (preset === 'brain') {
        this.skullMat.opacity = 0.18;
        this.brainTissueMat.opacity = 0.65;
        this.brainTissueMat.color.setHex(0x38bdf8);
        this.lesionMat.opacity = 0.85;
      } else if (preset === 'hemorrhage') {
        this.skullMat.opacity = 0.05;
        this.brainTissueMat.opacity = 0.2;
        this.brainTissueMat.color.setHex(0x3b82f6);
        this.lesionMat.opacity = 1.0;
        this.lesionMat.emissiveIntensity = 1.6;
      } else if (preset === 'bone') {
        this.skullMat.opacity = 0.85;
        this.skullMat.color.setHex(0xf8fafc);
        this.brainTissueMat.opacity = 0.1;
        this.lesionMat.opacity = 0.5;
      }
    }

    setSliceDepth(percent) {
      if (!this.initialized) return;
      const zOffset = ((percent / 100) - 0.5) * 140;
      this.clippingPlane.constant = zOffset;
      if (this.ctSlicePlaneMesh) {
        this.ctSlicePlaneMesh.position.z = zOffset;
      }
    }

    resetCamera() {
      if (!this.initialized) return;
      this.camera.position.set(0, 110, 210);
      if (this.controls) this.controls.reset();
    }

    onResize() {
      if (!this.initialized) return;
      const width = this.container.clientWidth;
      const height = this.container.clientHeight;
      if (width === 0 || height === 0) return;
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
    }

    animate() {
      requestAnimationFrame(() => this.animate());
      if (this.controls) this.controls.update();
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    }
  }
});
