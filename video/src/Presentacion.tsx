import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// Datos que se pueden cambiar desde el Studio o con --props al renderizar
export type PresentacionProps = {
  titulo: string;
  subtitulo: string;
  colorFondo: string;
  colorTexto: string;
};

export const Presentacion: React.FC<PresentacionProps> = ({
  titulo,
  subtitulo,
  colorFondo,
  colorTexto,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, durationInFrames } = useVideoConfig();

  const entrada = spring({ frame, fps, config: { damping: 200 } });
  const opacidadSub = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const salida = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const base = width / 20;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colorFondo,
        color: colorTexto,
        justifyContent: "center",
        alignItems: "center",
        textAlign: "center",
        fontFamily: "Helvetica, Arial, sans-serif",
        padding: base,
        opacity: salida,
      }}
    >
      <h1
        style={{
          fontSize: base * 1.4,
          margin: 0,
          transform: `translateY(${(1 - entrada) * 80}px)`,
          opacity: entrada,
        }}
      >
        {titulo}
      </h1>
      <p style={{ fontSize: base * 0.7, marginTop: base * 0.5, opacity: opacidadSub }}>
        {subtitulo}
      </p>
    </AbsoluteFill>
  );
};
