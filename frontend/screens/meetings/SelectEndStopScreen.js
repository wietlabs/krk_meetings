import * as React from "react";
import MapView, { Marker } from "react-native-maps";

export default function SelectEndStopScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const meetingUuid = route.params.meetingUuid;

  const mapRef = React.useRef();

  return (
    <MapView
      ref={mapRef}
      style={{
        width: "100%",
        height: "100%",
      }}
    ></MapView>
  );
}
