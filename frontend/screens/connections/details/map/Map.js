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

  const first_action = actions[0];
  const last_action = actions[actions.length - 1];

  const start_latlng = first_action.stops[0];
  const end_latlng = last_action.stops[last_action.stops.length - 1];

  const mapRef = React.useRef(null);

  const fitToContents = () => {
    var coords = actions.map((action) => action.stops).flat();
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
      {actions.map((action, i) => {
        const isWalking = action.type === "walking";
        const props = isWalking
          ? { strokeColor: "#00000066", lineDashPattern: [10, 10] }
          : { strokeColor: "#ff000088" };
        return (
          <Polyline
            key={i}
            coordinates={action.stops}
            strokeWidth={5}
            {...props}
          />
        );
      })}
    </MapView>
  );
}
