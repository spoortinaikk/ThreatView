
import React from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Tooltip
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

const COUNTRY_COORDINATES = {
  US: [39.5, -98.35],
  GB: [55.37, -3.43],
  IN: [20.59, 78.96],
  RU: [61.52, 105.31],
  CN: [35.86, 104.19],
  DE: [51.16, 10.45],
  FR: [46.22, 2.21],
  CA: [56.13, -106.34],
  AU: [-25.27, 133.77],
  JP: [36.2, 138.25],
  BR: [-14.23, -51.92],
  IS: [64.96, -19.02],
  CH: [46.81, 8.22],
  NL: [52.13, 5.29],
  IT: [41.87, 12.56],
  ES: [40.46, -3.74],
  KR: [35.9, 127.76],
  SG: [1.35, 103.81],
  UA: [48.37, 31.16],
  MX: [23.63, -102.55],
  AT: [47.52, 14.55],
  BG: [42.73, 25.48],
  HK: [22.32, 114.17],
  SC: [-4.68, 55.49],
  ZA: [-30.56, 22.94],
  LV: [56.88, 24.6],

  // Additional countries returned by the API
  BE: [50.50, 4.47],
  HU: [47.16, 19.50],
  NA: [-22.95, 18.49],
  TT: [10.69, -61.22],
  AE: [23.42, 53.85],
  EG: [26.82, 30.80],
  NO: [60.47, 8.46],
  PL: [51.92, 19.14],
  VN: [14.06, 108.28],
  MY: [4.21, 101.98],
  TH: [15.87, 100.99]
};

const SEVERITY_COLORS = {
  high: "#ff174d",
  medium: "#ffae22",
  low: "#54c7ec"
};

export default function ThreatMap({ countries = [], period = 1 }) {

  const points = countries.filter(
    (item) =>
      COUNTRY_COORDINATES[item.name] &&
      Number(item.count) > 0
  );

  const maxCount = Math.max(
    1,
    ...points.map((item) => Number(item.count))
  );

  return (
    <div style={{ width: "100%", height: "100%", minHeight: 350 }}>
      <div
        style={{
          color: "#9fb3c8",
          fontSize: "12px",
          marginBottom: "8px"
        }}
      >
        Country distribution · Last {period} day
        {Number(period) === 1 ? "" : "s"}
      </div>

      <MapContainer
        center={[25, 10]}
        zoom={1.5}
        minZoom={1}
        maxZoom={6}
        scrollWheelZoom={false}
        worldCopyJump
        style={{
          height: "calc(100% - 24px)",
          minHeight: 320,
          width: "100%",
          borderRadius: "12px",
          background: "#071426"
        }}
      >
        <TileLayer
          attribution="Tiles © Esri — Sources: Esri, HERE, Garmin, FAO, NOAA, USGS, EPA"
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        />

        {points.map((item) => {
          const high = Number(item.high || 0);
          const medium = Number(item.medium || 0);
          const low = Number(item.low || 0);

          // High severity always takes priority
          const severity =
            high > 0
              ? "high"
              : medium > 0
                ? "medium"
                : "low";

          const color = SEVERITY_COLORS[severity];

          const intensity = Number(item.count) / maxCount;
          const radius = 7 + intensity * 16;

          return (
            <React.Fragment key={item.name}>
              <CircleMarker
                center={COUNTRY_COORDINATES[item.name]}
                radius={radius + 5}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: 0.12,
                  weight: 1
                }}
              />

              <CircleMarker
                center={COUNTRY_COORDINATES[item.name]}
                radius={radius}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: 0.8,
                  weight: 2
                }}
              >
                <Tooltip>
                  <strong>{item.name}</strong>
                  <br />
                  Total: {Number(item.count).toLocaleString()}
                  <br />
                  High: {high.toLocaleString()}
                  <br />
                  Medium: {medium.toLocaleString()}
                  <br />
                  Low: {low.toLocaleString()}
                </Tooltip>
              </CircleMarker>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
}
