import { Composition } from "remotion";
import { Presentacion, PresentacionProps } from "./Presentacion";

const defaultProps: PresentacionProps = {
  titulo: "Contabilidad para tu unipersonal",
  subtitulo: "Apertura, impuestos y liquidaciones al día",
  colorFondo: "#0f3d3e",
  colorTexto: "#ffffff",
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Horizontal 16:9 (YouTube, web) */}
      <Composition
        id="Presentacion"
        component={Presentacion}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
      />
      {/* Vertical 9:16 (Reels, TikTok, Stories) */}
      <Composition
        id="PresentacionVertical"
        component={Presentacion}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultProps}
      />
    </>
  );
};
