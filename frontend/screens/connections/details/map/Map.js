import * as React from "react";
import MapView, { Marker, Polyline } from "react-native-maps";
import { filterTransfers } from "../../../../utils";

const edgePadding = {
  top: 150,
  bottom: 120,
  left: 100,
  right: 100,
};

export default function ConnectionDetailsMap({ connection }) {
  const actions = connection.actions;
  const transfers = filterTransfers(actions);

  const first_transfer = transfers[0];
  const last_transfer = transfers[transfers.length - 1];

  const start_latlng = first_transfer.stops[0];
  const end_latlng = last_transfer.stops[last_transfer.stops.length - 1];

  const mapRef = React.useRef(null);

  const fitToContents = () => {
    var coords = transfers.map((transfer) => transfer.stops).flat();
    mapRef.current.fitToCoordinates(coords, {
      edgePadding: edgePadding,
      animated: false,
    });
  };

  return (
    <MapView
      ref={mapRef}
      onLayout={fitToContents}
      style={{ width: "100%", height: "40%" }}
    >
      <Marker coordinate={start_latlng} pinColor="green" />
      <Marker coordinate={end_latlng} pinColor="red" />
      {transfers.map((transfer, i) => {
        return (
          <Polyline
            key={i}
            coordinates={transfer.stops}
            strokeColor="#ff000088"
            strokeWidth={5}
          />
        );
      })}
    </MapView>
  );
}
