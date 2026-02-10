import { useState } from "react";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import InsertDriveFileOutlinedIcon from "@mui/icons-material/InsertDriveFileOutlined";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";

interface ImageUploaderProps {
  onFileSelect: (file: File | null) => void;
}

const UploadIcon = () => (
  <CloudUploadOutlinedIcon sx={{ fontSize: 40, color: "text.secondary" }} />
);

const FileIcon = () => (
  <InsertDriveFileOutlinedIcon sx={{ fontSize: 40, color: "primary.main" }} />
);

const ImageUploader = ({ onFileSelect }: ImageUploaderProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFile = (selectedFile: File) => {
    setFile(selectedFile);
    onFileSelect(selectedFile);
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const onDragLeave = () => setIsDragOver(false);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const removeFile = () => {
    setFile(null);
    onFileSelect(null);
  };

  return (
    <Box>
      {!file ? (
        <Paper
          variant="outlined"
          sx={{
            p: 3,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 1.5,
            borderStyle: "dashed",
            cursor: "pointer",
            bgcolor: isDragOver ? "action.hover" : "background.paper",
            transition: "background-color .2s ease",
          }}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => document.getElementById("dropzone-file")?.click()}
        >
          <UploadIcon />
          <Typography variant="body2" color="text.secondary">
            Seret & Lepas, atau{" "}
            <Box component="span" color="primary.main" fontWeight={600}>
              Pilih File
            </Box>
          </Typography>
          <input
            id="dropzone-file"
            type="file"
            style={{ display: "none" }}
            onChange={onFileChange}
            accept="image/png, image/jpeg"
          />
        </Paper>
      ) : (
        <Paper
          variant="outlined"
          sx={{
            p: 2.5,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Stack direction="row" spacing={1.5} alignItems="center">
            <FileIcon />
            <Box>
              <Typography variant="body2" fontWeight={600}>
                {file.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {(file.size / 1024).toFixed(2)} KB
              </Typography>
            </Box>
          </Stack>
          <IconButton
            color="inherit"
            onClick={removeFile}
            aria-label="hapus file"
          >
            <CloseRoundedIcon />
          </IconButton>
        </Paper>
      )}
    </Box>
  );
};

export default ImageUploader;
