import { useState } from "react";
import axios from "axios";
import ImageUploader from "./components/ImageUploader";
import Tabs from "./components/Tabs";
import Button from "@mui/material/Button";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Container from "@mui/material/Container";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Divider from "@mui/material/Divider";
import CircularProgress from "@mui/material/CircularProgress";
import ResultsDisplay from "./features/results/ResultsDisplay";

// Definisikan tipe data untuk hasil analisis agar lebih aman
interface ImageQualityAssessment {
  brisque: number;
  niqe: number;
}

interface PredictionWithConfidence {
  label: string;
  confidence: number;
}

interface Predictions {
  knn: PredictionWithConfidence[];
  svm: PredictionWithConfidence[];
  cosine: PredictionWithConfidence[];
}

interface AnalysisPipelineA {
  iqa: ImageQualityAssessment | null;
  predictions: Predictions | null;
}

interface AnalysisPipelineB {
  restored_image_url: string;
  iqa: ImageQualityAssessment | null;
  predictions: Predictions | null;
}

interface AnalysisResult {
  original_image_url: string;
  pipeline_a: AnalysisPipelineA | null;
  pipeline_b: AnalysisPipelineB | null;
  probe_coords: { x: number; y: number } | null;
}

function App() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [activeTab, setActiveTab] = useState<string>("upload");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);

  const handleAnalysis = async () => {
    if (!imageFile) return;

    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append("image", imageFile);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/recognize",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setAnalysisResult(response.data);
      setActiveTab("result"); // Pindah ke tab hasil setelah berhasil
    } catch (err) {
      console.error("Error during analysis:", err);
      setError(
        "Gagal melakukan analisis. Pastikan server backend berjalan dan coba lagi."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar
        position="static"
        color="transparent"
        enableColorOnDark
        sx={{
          backdropFilter: "blur(6px)",
          bgcolor: "rgba(18,18,18,0.6)",
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Toolbar>
          <Container
            maxWidth="lg"
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <Typography variant="h6" fontWeight={800} letterSpacing={0.5}>
              VisioRecog
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Face Recognition & Restoration Analysis
            </Typography>
          </Container>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Stack spacing={3}>
          <Paper
            variant="outlined"
            sx={{ p: 2.5, bgcolor: "background.paper" }}
          >
            <Tabs
              tabs={[
                { key: "upload", label: "Unggah" },
                { key: "result", label: "Hasil" },
              ]}
              value={activeTab}
              onChange={setActiveTab}
            />
          </Paper>

          {activeTab === "upload" && (
            <Paper variant="outlined" sx={{ p: 3 }}>
              <Stack spacing={3}>
                <ImageUploader onFileSelect={setImageFile} />
                <Divider light />
                <Box textAlign="center">
                  <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    disabled={!imageFile || isLoading}
                    onClick={handleAnalysis}
                    startIcon={
                      isLoading ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : null
                    }
                  >
                    {isLoading ? "Menganalisis..." : "Mulai Analisis"}
                  </Button>
                </Box>
              </Stack>
            </Paper>
          )}

          {activeTab === "result" && (
            <Paper variant="outlined" sx={{ p: 3 }}>
              {error && <Typography color="error">{error}</Typography>}
              {analysisResult ? (
                <ResultsDisplay result={analysisResult} />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Belum ada hasil. Unggah gambar dan mulai analisis terlebih
                  dahulu.
                </Typography>
              )}
            </Paper>
          )}
        </Stack>
      </Container>
    </Box>
  );
}

export default App;
