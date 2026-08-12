import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, LayoutGrid, Zap, BrainCircuit, Activity, Settings2, Download, CheckCircle, FileJson, Trash2 } from 'lucide-react';
import './index.css';

function App() {
  const [scans, setScans] = useState([]);
  const [selectedScanId, setSelectedScanId] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [viewMode, setViewMode] = useState('2d');
  const [windowPreset, setWindowPreset] = useState('brain');
  const [imageUrls, setImageUrls] = useState({});
  const [showCam, setShowCam] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const fileInputRef = useRef(null);

  useEffect(() => {
    fetch('/api/v1/scans')
      .then(r => r.json())
      .then(data => setScans(data))
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedScanId) {
      setAnalysis(null);
      setShowCam(false);
      fetchImage(selectedScanId, windowPreset);
    }
  }, [selectedScanId, windowPreset]);

  const fetchImage = async (id, preset) => {
    try {
      const res = await fetch(`/api/v1/scans/${id}/image?preset=${preset}`);
      if (res.ok) {
        const data = await res.json();
        setImageUrls(prev => ({ ...prev, [preset]: data.image_data_url }));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleLoadDemo = async () => {
    try {
      const res = await fetch('/api/v1/scans/load_demo', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setScans(prev => [data, ...prev.filter(s => s.scan_id !== data.scan_id)]);
        setSelectedScanId(data.scan_id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('/api/v1/scans/upload', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setScans(prev => [data, ...prev]);
        setSelectedScanId(data.scan_id);
      }
    } catch (err) {
      console.error(err);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const triggerUpload = () => {
    if (fileInputRef.current) fileInputRef.current.click();
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    try {
      const res = await fetch(`/api/v1/scans/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setScans(prev => prev.filter(s => s.scan_id !== id));
        if (selectedScanId === id) setSelectedScanId(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedScanId) return;
    setIsAnalyzing(true);
    try {
      const res = await fetch(`/api/v1/scans/${selectedScanId}/analyze`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setAnalysis(data);
        if (data.heatmap_data_url) {
          setShowCam(true);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadMD = () => {
    if (!analysis?.report_markdown) return;
    const blob = new Blob([analysis.report_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${selectedScanId}.md`;
    a.click();
  };

  const handleDownloadJSON = () => {
    if (!analysis?.radiology_report) return;
    const blob = new Blob([JSON.stringify(analysis.radiology_report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${selectedScanId}.json`;
    a.click();
  };

  const findings = analysis?.decision_support;

  return (
    <div className="app-container">
      <header className="header">
        <div className="brand">
          <div className="brand-logo">R</div>
          <h1 style={{ fontSize: '1.2rem', fontWeight: 600 }}>RADIS AI Workstation</h1>
          <span style={{ fontSize: '0.7rem', padding: '2px 8px', background: 'var(--border-glass)', borderRadius: '12px' }}>v2.0.0</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--severity-low)' }}></div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-main)', fontWeight: 500 }}>Engine Connected</span>
        </div>
      </header>

      <main className="main-content">
        
        <section className="panel animate-in" style={{ animationDelay: '0.1s' }}>
          <div className="panel-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Upload size={18} /> Upload & Queue
            </div>
          </div>
          <div className="panel-body">
            <input 
              type="file" 
              accept=".dcm" 
              style={{ display: 'none' }} 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
            />
            <div className="dropzone" onClick={triggerUpload}>
              <Upload size={32} color="var(--accent-cyan)" />
              <div>
                <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>Click or Drop DICOM</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Supports .dcm files</div>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn" style={{ flex: 1 }} onClick={triggerUpload}>
                Add File
              </button>
              <button className="btn" style={{ flex: 1 }} onClick={handleLoadDemo}>
                <Zap size={16} /> Demo
              </button>
            </div>

            <div style={{ marginTop: '16px', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '0.5px' }}>
              PATIENT SCANS
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {scans.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No scans in queue
                </div>
              ) : (
                scans.map(scan => (
                  <div 
                    key={scan.scan_id} 
                    className={`scan-item ${selectedScanId === scan.scan_id ? 'active' : ''}`}
                    onClick={() => setSelectedScanId(scan.scan_id)}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{scan.scan_id}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        {new Date(scan.uploaded_at || new Date()).toLocaleTimeString()}
                      </div>
                    </div>
                    <button 
                      onClick={(e) => handleDelete(e, scan.scan_id)}
                      style={{ background: 'transparent', border: 'none', color: 'var(--severity-high)', cursor: 'pointer', padding: '4px' }}
                      title="Remove scan"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        <section className="panel animate-in" style={{ animationDelay: '0.2s' }}>
          <div className="panel-header" style={{ padding: '8px 16px' }}>
            <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.05)', padding: '4px', borderRadius: 'var(--radius-sm)' }}>
              <button 
                className={`btn ${viewMode === '2d' ? 'btn-primary' : ''}`} 
                style={{ border: 'none', background: viewMode === '2d' ? 'var(--border-glass)' : 'transparent', color: viewMode === '2d' ? 'var(--text-main)' : 'var(--text-muted)' }}
                onClick={() => setViewMode('2d')}
              >
                2D Slice
              </button>
              <button 
                className={`btn ${viewMode === '3d' ? 'btn-primary' : ''}`}
                style={{ border: 'none', background: viewMode === '3d' ? 'var(--border-glass)' : 'transparent', color: viewMode === '3d' ? 'var(--text-main)' : 'var(--text-muted)' }}
                onClick={() => setViewMode('3d')}
              >
                3D Volumetric
              </button>
            </div>
            
            {viewMode === '2d' && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className={`btn ${windowPreset === 'brain' ? 'active' : ''}`} onClick={() => setWindowPreset('brain')} style={windowPreset === 'brain' ? {background: 'var(--border-glass)', color: 'var(--text-main)', fontWeight: 600} : {}}>Brain</button>
                <button className={`btn ${windowPreset === 'bone' ? 'active' : ''}`} onClick={() => setWindowPreset('bone')} style={windowPreset === 'bone' ? {background: 'var(--border-glass)', color: 'var(--text-main)', fontWeight: 600} : {}}>Bone</button>
                <button className={`btn ${windowPreset === 'subdural' ? 'active' : ''}`} onClick={() => setWindowPreset('subdural')} style={windowPreset === 'subdural' ? {background: 'var(--border-glass)', color: 'var(--text-main)', fontWeight: 600} : {}}>Subdural</button>
                <button className={`btn ${showCam ? 'active' : ''}`} onClick={() => setShowCam(!showCam)} style={showCam ? {background: 'var(--border-glass)', color: 'var(--text-main)', fontWeight: 600} : {}}>Grad-CAM</button>
              </div>
            )}
          </div>
          
          <div className="panel-body" style={{ padding: '12px' }}>
            <div className="canvas-wrapper">
              {viewMode === '3d' ? (
                <div style={{ color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                  <Activity size={48} opacity={0.2} />
                  <span>3D Volumetric Rendering (Coming Soon)</span>
                </div>
              ) : !imageUrls[windowPreset] ? (
                <div style={{ color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                  <Activity size={48} opacity={0.2} />
                  <span>{selectedScanId ? 'Loading DICOM...' : 'Select a scan to view'}</span>
                </div>
              ) : (
                <>
                  <img src={imageUrls[windowPreset]} alt="DICOM Slice" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                  {showCam && analysis?.heatmap_data_url && (
                    <img src={analysis.heatmap_data_url} alt="Grad-CAM" style={{ position: 'absolute', maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', opacity: 0.6, mixBlendMode: 'screen' }} />
                  )}
                </>
              )}
              
              {selectedScanId && (
                <div style={{ position: 'absolute', top: 12, left: 12, background: 'var(--bg-card)', padding: '6px 12px', borderRadius: '4px', border: '1px solid var(--border-glass)', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  STUDY: {selectedScanId}
                </div>
              )}
            </div>
            <button className="btn btn-primary" style={{ width: '100%', padding: '12px', fontSize: '0.95rem', fontWeight: 600 }} onClick={handleRunAnalysis} disabled={!selectedScanId || isAnalyzing}>
              {isAnalyzing ? <Activity size={18} className="animate-spin" /> : <BrainCircuit size={18} />}
              {isAnalyzing ? 'Analyzing Scan...' : 'Run AI Analysis'}
            </button>
          </div>
        </section>

        <section className="panel animate-in" style={{ animationDelay: '0.3s' }}>
          <div className="panel-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={18} /> Clinical Findings
            </div>
          </div>
          <div className="panel-body">
            {!findings ? (
              <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '32px 16px', fontSize: '0.9rem' }}>
                Run AI analysis to generate findings and report.
              </div>
            ) : (
              <div className="animate-in" style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1 }}>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div style={{ padding: '6px 16px', borderRadius: '24px', fontSize: '0.8rem', fontWeight: 700, background: 'var(--bg-card)', color: 'var(--severity-high)', border: '2px solid var(--severity-high)', letterSpacing: '0.5px' }}>
                    URGENCY: {findings.urgency_level || 'UNKNOWN'}
                  </div>
                </div>

                <div style={{ padding: '16px', background: 'var(--border-glass)', borderLeft: '4px solid var(--accent-cyan)', borderRadius: '0 var(--radius-sm) var(--radius-sm) 0', fontSize: '1rem', fontWeight: 500, color: 'var(--text-main)', lineHeight: 1.6 }}>
                  {findings.workflow_recommendation || 'No recommendation available.'}
                </div>

                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '8px', letterSpacing: '0.5px' }}>
                  DETECTED PATHOLOGIES
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {(!analysis?.decision_support?.findings || analysis.decision_support.findings.length === 0) ? (
                    <div style={{ color: 'var(--text-main)', fontSize: '0.9rem', fontStyle: 'italic' }}>No significant pathologies detected.</div>
                  ) : (
                    analysis.decision_support.findings.map((p, i) => (
                      <div key={i} style={{ padding: '16px', background: 'var(--bg-dark)', color: 'var(--text-inverse)', border: '1px solid var(--border-glass)', borderRadius: 'var(--radius-md)', boxShadow: 'var(--shadow-card)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontSize: '0.95rem', fontWeight: 600 }}>
                          <span style={{ textTransform: 'capitalize' }}>{p.label}</span>
                          <span style={{ color: 'var(--text-inverse)', opacity: 0.9 }}>{(p.probability * 100).toFixed(1)}%</span>
                        </div>
                        <div style={{ height: '6px', background: 'var(--bg-card)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${p.probability * 100}%`, background: 'var(--accent-cyan)' }}></div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div style={{ marginTop: 'auto', display: 'flex', gap: '8px' }}>
                  <button className="btn" style={{ flex: 1, fontWeight: 600, color: 'var(--text-main)', borderColor: 'var(--text-main)' }} onClick={handleDownloadMD} disabled={!analysis?.report_markdown}>
                    <Download size={16} /> MD
                  </button>
                  <button className="btn" style={{ flex: 1, fontWeight: 600, color: 'var(--text-main)', borderColor: 'var(--text-main)' }} onClick={handleDownloadJSON} disabled={!analysis?.radiology_report}>
                    <FileJson size={16} /> JSON
                  </button>
                  <button className="btn btn-primary" style={{ flex: 2, fontWeight: 600 }}><CheckCircle size={16} /> Approve</button>
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
