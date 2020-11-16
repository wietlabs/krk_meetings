import * as React from "react";
import MapView, { Marker } from "react-native-maps";
import { getStops, findMeetingPoints } from "../../api/ConnectionsApi";
import { getMeetingDetails } from "../../api/MeetingsApi";
import { getMeetingMembersStopNames, getStopsByNames } from "../../utils";

const initialRegion = {
  latitude: 50.04,
  longitude: 19.96,
  latitudeDelta: 0.3,
  longitudeDelta: 0.4,
};

const padding = {
  top: 100,
  bottom: 100,
  left: 100,
  right: 100,
};

export default function SelectEndStopScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const meetingUuid = route.params.meetingUuid;

  const mapRef = React.useRef();

  const [locations, setLocations] = React.useState([]);
  const [points, setPoints] = React.useState([]);

  const refresh = async () => {
    // TODO: use Promise.all

    const stops = await getStops();

    const meeting = await getMeetingDetails(meetingUuid, userUuid);

    const stopNames = getMeetingMembersStopNames(meeting);

    const locations = await getStopsByNames(stopNames, stops);
    setLocations(locations);

    const query = { startStopNames: stopNames, metric: "square" };
    const points = await findMeetingPoints(query);
    setPoints(points);
  };

  React.useEffect(() => {
    refresh();
  }, []);

  React.useEffect(() => {
    const coords = [...locations, ...points];
    fitToContents(coords);
  }, [locations, points]);

  const fitToContents = (coords) => {
    mapRef.current.fitToCoordinates(coords, {
      animated: true,
      edgePadding: padding,
    });
  };

  return (
    <MapView
      ref={mapRef}
      initialRegion={initialRegion}
      maxZoomLevel={18}
      moveOnMarkerPress={false}
      style={{
        width: "100%",
        height: "100%",
      }}
    >
      {locations.map((location, i) => (
        <Marker key={"location-" + i} coordinate={location} pinColor="red" />
      ))}
      {points.map((point, i) => (
        <Marker key={"point-" + i} coordinate={point} pinColor="green" />
      ))}
    </MapView>
  );
}
