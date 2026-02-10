import { useState } from 'react';
import axios from 'axios';
import { Box, Button, Typography, Paper, CircularProgress, Alert } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import EvaluationReport from './EvaluationReport';

const EvaluationPage = () => {
  const [jsonFile, setJsonFile] = useState<File | null>(null);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);
  const [evaluationResult, setEvaluationResult] = useState<any | null>(null);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type === 'application/json') {
        setJsonFile(file);
        setEvaluationError(null);
      } else {
        setEvaluationError('File harus dalam format JSON.');
        setJsonFile(null);
      }
    }
  };

  const handleEvaluation = async () => {
    if (!jsonFile) return;

    setIsEvaluating(true);
    setEvaluationError(null);
    setEvaluationResult(null);

    const formData = new FormData();
    formData.append('json_file', jsonFile);

    try {
      const response = await axios.post('http://127.0.0.1:8000/evaluate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setEvaluationResult(response.data);
    } catch (err: any) {
      console.error('Error during evaluation:', err);
      const errorMsg = err.response?.data?.detail || 'Gagal melakukan evaluasi. Pastikan server backend berjalan dan file JSON valid.';
      setEvaluationError(errorMsg);
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <Box>
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Unggah File Evaluasi
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Pilih file JSON yang berisi dataset evaluasi (embedding, ground truth, dll).
        </Typography>
        
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadFileIcon />}
        >
          Pilih File JSON
          <input
            type="file"
            hidden
            accept="application/json"
            onChange={handleFileChange}
          />
        </Button>

        {jsonFile && (
          <Typography sx={{ mt: 2, fontStyle: 'italic' }}>
            File terpilih: {jsonFile.name}
          </Typography>
        )}

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            disabled={!jsonFile || isEvaluating}
            onClick={handleEvaluation}
            startIcon={isEvaluating ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {isEvaluating ? 'Mengevaluasi...' : 'Mulai Evaluasi'}
          </Button>
        </Box>
      </Paper>

      {evaluationError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {evaluationError}
        </Alert>
      )}

      {evaluationResult && (
        <EvaluationReport report={evaluationResult} />
      )}
    </Box>
  );
};

export default EvaluationPage;
