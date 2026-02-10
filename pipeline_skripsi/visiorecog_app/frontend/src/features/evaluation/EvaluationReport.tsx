import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from "@mui/material";

// Definisikan tipe data untuk props, ini harus cocok dengan struktur dari backend
interface EvaluationMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: number[][];
}

interface EvaluationResult {
  knn: EvaluationMetrics;
  svm: EvaluationMetrics;
  cosine: EvaluationMetrics;
}

interface ReportData {
  summary: {
    total_items: number;
    restoration_success_rate: number;
  };
  iqa_comparison: {
    original: { avg_brisque: number; avg_niqe: number };
    restored: { avg_brisque: number; avg_niqe: number };
  };
  evaluation_results: {
    without_restoration: EvaluationResult;
    with_restoration: EvaluationResult;
  };
  class_labels: string[];
}

interface EvaluationReportProps {
  report: ReportData;
}

const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
const formatNumber = (value: number) => value.toFixed(2);

const SummaryCard = ({
  title,
  value,
  unit = "",
}: {
  title: string;
  value: string | number;
  unit?: string;
}) => (
  <Paper variant="outlined" sx={{ p: 2, textAlign: "center", height: "100%" }}>
    <Typography variant="h6" color="text.secondary">
      {title}
    </Typography>
    <Typography variant="h4" fontWeight="bold">
      {value}
      {unit}
    </Typography>
  </Paper>
);

import ConfusionMatrixPlot from "./ConfusionMatrixPlot";

const EvaluationReport = ({ report }: EvaluationReportProps) => {
  const { summary, iqa_comparison, evaluation_results, class_labels } = report;

  const renderMetricRow = (
    metricName: Exclude<keyof EvaluationMetrics, "confusion_matrix">,
    displayName: string
  ) => {
    // ... (fungsi ini tidak berubah)
    const format =
      metricName === "accuracy" ||
      metricName === "precision" ||
      metricName === "recall" ||
      metricName === "f1_score"
        ? formatPercent
        : (v: any) => v;

    return (
      <TableRow key={metricName}>
        <TableCell>
          <strong>{displayName}</strong>
        </TableCell>
        <TableCell align="right">
          {format(evaluation_results.without_restoration.knn[metricName])}
        </TableCell>
        <TableCell align="right">
          {format(evaluation_results.with_restoration.knn[metricName])}
        </TableCell>
        <TableCell align="right">
          {format(evaluation_results.without_restoration.svm[metricName])}
        </TableCell>
        <TableCell align="right">
          {format(evaluation_results.with_restoration.svm[metricName])}
        </TableCell>
        <TableCell align="right">
          {format(evaluation_results.without_restoration.cosine[metricName])}
        </TableCell>
        <TableCell align="right">
          {format(evaluation_results.with_restoration.cosine[metricName])}
        </TableCell>
      </TableRow>
    );
  };

  return (
    <Box>
      {/* ... (Bagian Ringkasan dan Tabel tidak berubah) ... */}
      <Typography variant="h5" gutterBottom>
        Ringkasan Evaluasi
      </Typography>
      <Box
        sx={{
          display: "flex",
          gap: 2,
          flexDirection: { xs: "column", sm: "row" },
          mb: 4,
        }}
      >
        <Box sx={{ flex: 1 }}>
          <SummaryCard title="Total Data" value={summary.total_items} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <SummaryCard
            title="Restorasi Berhasil"
            value={formatPercent(summary.restoration_success_rate)}
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <Paper variant="outlined" sx={{ p: 2, textAlign: "center" }}>
            <Typography variant="subtitle1" color="text.secondary">
              Avg. BRISQUE
            </Typography>
            <Chip
              label={`Original: ${formatNumber(
                iqa_comparison.original.avg_brisque
              )}`}
              sx={{ mr: 1 }}
            />
            <Chip
              label={`Restored: ${formatNumber(
                iqa_comparison.restored.avg_brisque
              )}`}
              color="success"
            />
            <Typography
              variant="subtitle1"
              color="text.secondary"
              sx={{ mt: 1 }}
            >
              Avg. NIQE
            </Typography>
            <Chip
              label={`Original: ${formatNumber(
                iqa_comparison.original.avg_niqe
              )}`}
              sx={{ mr: 1 }}
            />
            <Chip
              label={`Restored: ${formatNumber(
                iqa_comparison.restored.avg_niqe
              )}`}
              color="success"
            />
          </Paper>
        </Box>
      </Box>

      {/* Bagian Tabel Perbandingan */}
      <Typography variant="h5" gutterBottom>
        Perbandingan Metrik Performa
      </Typography>
      <TableContainer component={Paper} variant="outlined" sx={{ mb: 4 }}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Metrik</TableCell>
              <TableCell align="center" colSpan={2}>
                KNN
              </TableCell>
              <TableCell align="center" colSpan={2}>
                SVM
              </TableCell>
              <TableCell align="center" colSpan={2}>
                Cosine
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell />
              <TableCell align="right">Original</TableCell>
              <TableCell align="right">Restored</TableCell>
              <TableCell align="right">Original</TableCell>
              <TableCell align="right">Restored</TableCell>
              <TableCell align="right">Original</TableCell>
              <TableCell align="right">Restored</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {renderMetricRow("accuracy", "Akurasi")}
            {renderMetricRow("precision", "Presisi")}
            {renderMetricRow("recall", "Recall")}
            {renderMetricRow("f1_score", "F1-Score")}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Bagian Confusion Matrix */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Confusion Matrix
      </Typography>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
        <Box
          sx={{
            flex: { xs: "1 1 100%", md: "1 1 calc(50% - 16px)" },
            minWidth: 0,
          }}
        >
          <ConfusionMatrixPlot
            title="KNN (Original)"
            matrix={evaluation_results.without_restoration.knn.confusion_matrix}
            labels={class_labels}
          />
        </Box>
        <Box
          sx={{
            flex: { xs: "1 1 100%", md: "1 1 calc(50% - 16px)" },
            minWidth: 0,
          }}
        >
          <ConfusionMatrixPlot
            title="KNN (Restored)"
            matrix={evaluation_results.with_restoration.knn.confusion_matrix}
            labels={class_labels}
          />
        </Box>
        <Box
          sx={{
            flex: { xs: "1 1 100%", md: "1 1 calc(50% - 16px)" },
            minWidth: 0,
          }}
        >
          <ConfusionMatrixPlot
            title="SVM (Original)"
            matrix={evaluation_results.without_restoration.svm.confusion_matrix}
            labels={class_labels}
          />
        </Box>
        <Box
          sx={{
            flex: { xs: "1 1 100%", md: "1 1 calc(50% - 16px)" },
            minWidth: 0,
          }}
        >
          <ConfusionMatrixPlot
            title="SVM (Restored)"
            matrix={evaluation_results.with_restoration.svm.confusion_matrix}
            labels={class_labels}
          />
        </Box>
        <Box
          sx={{
            flex: { xs: "1 1 100%", md: "1 1 calc(50% - 16px)" },
            minWidth: 0,
          }}
        >
          <ConfusionMatrixPlot
            title="Cosine (Original)"
            matrix={
              evaluation_results.without_restoration.cosine.confusion_matrix
            }
            labels={class_labels}
          />
        </Box>
        <Box
          sx={{
            flex: { xs: "1 1 100%", md: "1 1 calc(50% - 16px)" },
            minWidth: 0,
          }}
        >
          <ConfusionMatrixPlot
            title="Cosine (Restored)"
            matrix={evaluation_results.with_restoration.cosine.confusion_matrix}
            labels={class_labels}
          />
        </Box>
      </Box>
    </Box>
  );
};

export default EvaluationReport;
