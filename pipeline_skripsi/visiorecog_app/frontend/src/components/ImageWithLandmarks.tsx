import { useState, useRef, useEffect } from "react";
import Box from "@mui/material/Box";

interface FacialArea {
  x: number;
  y: number;
  w: number;
  h: number;
  left_eye: [number, number];
  right_eye: [number, number];
  nose: [number, number];
  mouth_left: [number, number];
  mouth_right: [number, number];
  image_width?: number;
  image_height?: number;
}

interface Props {
  src: string;
  landmarks: FacialArea | null;
  alt: string;
  originalImageSize?: { width: number; height: number };
}

const landmarkColors = {
  left_eye: "#FFD700",
  right_eye: "#FFD700",
  nose: "#32CD32",
  mouth_left: "#FF4500",
  mouth_right: "#FF4500",
};

const ImageWithLandmarks = ({
  src,
  landmarks,
  alt,
  originalImageSize,
}: Props) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setImageLoaded(false);
  }, [src]);

  const handleImageLoad = () => {
    setTimeout(() => {
      setImageLoaded(true);
    }, 50);
  };

  const renderLandmarks = () => {
    if (!landmarks || !imageLoaded || !imgRef.current || !overlayRef.current) {
      return null;
    }

    const imgElement = imgRef.current;
    const imgRect = imgElement.getBoundingClientRect();
    const overlayRect = overlayRef.current.getBoundingClientRect();

    const naturalWidth = imgElement.naturalWidth;
    const naturalHeight = imgElement.naturalHeight;

    const renderedWidth = imgRect.width;
    const renderedHeight = imgRect.height;

    const imgOffsetX = imgRect.left - overlayRect.left;
    const imgOffsetY = imgRect.top - overlayRect.top;

    const scaleX = renderedWidth / naturalWidth;
    const scaleY = renderedHeight / naturalHeight;

    console.log("Debug Info:", {
      naturalSize: `${naturalWidth}x${naturalHeight}`,
      renderedSize: `${renderedWidth.toFixed(2)}x${renderedHeight.toFixed(2)}`,
      offset: `${imgOffsetX.toFixed(2)}, ${imgOffsetY.toFixed(2)}`,
      scale: `${scaleX.toFixed(4)}, ${scaleY.toFixed(4)}`,
    });

    const { left_eye, right_eye, nose, mouth_left, mouth_right } = landmarks;
    const points = { left_eye, right_eye, nose, mouth_left, mouth_right };

    console.log("🔍 LANDMARKS DEBUG:", {
      hasImageWidth: "image_width" in landmarks,
      hasImageHeight: "image_height" in landmarks,
      imageWidth: landmarks.image_width,
      imageHeight: landmarks.image_height,
    });

    return Object.entries(points).map(([key, coords]) => {
      let [x, y] = coords;

      let referenceWidth = naturalWidth;
      let referenceHeight = naturalHeight;
      let scaleMethod = "natural";

      if (
        landmarks.image_width &&
        landmarks.image_height &&
        landmarks.image_width > 0 &&
        landmarks.image_height > 0
      ) {
        referenceWidth = landmarks.image_width;
        referenceHeight = landmarks.image_height;
        scaleMethod = "from_backend";
        console.log(
          `✅ Using reference size from backend: ${referenceWidth}x${referenceHeight}`
        );
      } else if (
        originalImageSize &&
        originalImageSize.width > 0 &&
        originalImageSize.height > 0
      ) {
        referenceWidth = originalImageSize.width;
        referenceHeight = originalImageSize.height;
        scaleMethod = "from_props";
        console.log(
          `⚠️ Using reference size from props: ${referenceWidth}x${referenceHeight}`
        );
      } else if (x > naturalWidth || y > naturalHeight) {
        const allCoords = Object.values(points).flat();
        const maxCoord = Math.max(...allCoords);

        if (maxCoord > 256) {
          referenceWidth = referenceHeight = 512;
        } else if (maxCoord > 128) {
          referenceWidth = referenceHeight = 256;
        } else {
          referenceWidth = referenceHeight = 128;
        }

        scaleMethod = "auto_detected";
        console.warn(
          `🔧 AUTO-DETECTED reference size: ${referenceWidth}x${referenceHeight} (max coord: ${maxCoord})`
        );
      }

      if (
        referenceWidth !== naturalWidth ||
        referenceHeight !== naturalHeight
      ) {
        const scaleToNatural_X = naturalWidth / referenceWidth;
        const scaleToNatural_Y = naturalHeight / referenceHeight;

        const oldX = x;
        const oldY = y;

        x = x * scaleToNatural_X;
        y = y * scaleToNatural_Y;

        console.log(`📐 ${key} [${scaleMethod}]:`, {
          original: `(${oldX}, ${oldY})`,
          referenceSize: `${referenceWidth}x${referenceHeight}`,
          naturalSize: `${naturalWidth}x${naturalHeight}`,
          scaleFactor: `${scaleToNatural_X.toFixed(
            4
          )}, ${scaleToNatural_Y.toFixed(4)}`,
          result: `(${x.toFixed(2)}, ${y.toFixed(2)})`,
        });
      }

      if (x < 0 || y < 0 || x > naturalWidth || y > naturalHeight) {
        console.warn(`${key} out of bounds:`, {
          x: x.toFixed(2),
          y: y.toFixed(2),
          naturalWidth,
          naturalHeight,
        });
        return null;
      }

      const scaledX = x * scaleX;
      const scaledY = y * scaleY;

      const finalX = scaledX + imgOffsetX;
      const finalY = scaledY + imgOffsetY;

      console.log(`🎯 ${key} FINAL:`, {
        afterScaling: `(${x.toFixed(2)}, ${y.toFixed(2)})`,
        renderedPos: `(${scaledX.toFixed(2)}, ${scaledY.toFixed(2)})`,
        finalPos: `(${finalX.toFixed(2)}, ${finalY.toFixed(2)})`,
      });

      return (
        <Box
          key={key}
          sx={{
            position: "absolute",
            left: `${finalX}px`,
            top: `${finalY}px`,
            width: "16px",
            height: "16px",
            borderRadius: "50%",
            backgroundColor: landmarkColors[key as keyof typeof landmarkColors],
            transform: "translate(-50%, -50%)",
            border: "3px solid #fff",
            boxShadow: "0 0 0 2px #000, 0 0 10px rgba(0,0,0,0.6)",
            zIndex: 10,
            pointerEvents: "none",
          }}
        />
      );
    });
  };

  return (
    <Box
      ref={containerRef}
      sx={{
        position: "relative",
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#1a1a1a",
        overflow: "hidden",
      }}
    >
      <img
        ref={imgRef}
        src={src}
        alt={alt}
        onLoad={handleImageLoad}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          display: "block",
          imageRendering: "pixelated",
        }}
      />
      <Box
        ref={overlayRef}
        sx={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
      >
        {renderLandmarks()}
      </Box>
    </Box>
  );
};

export default ImageWithLandmarks;
