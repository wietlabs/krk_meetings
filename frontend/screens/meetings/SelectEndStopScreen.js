import * as React from "react";
import { View } from "react-native";
import MapView, { Marker } from "react-native-maps";
import { Divider, Button, RadioButton, Text } from "react-native-paper";
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

const availableMetrics = [
  {
    name: "max",
    label: "Szybko",
  },
  {
    name: "sum",
    label: "Wygodnie",
  },
  {
    name: "square",
    label: "Uczciwie",
  },
];

export default function SelectEndStopScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const meetingUuid = route.params.meetingUuid;

  const mapRef = React.useRef();

  const [locations, setLocations] = React.useState([]);
  const [points, setPoints] = React.useState([]);
  const [metric, setMetric] = React.useState("square");
  const [loading, setLoading] = React.useState(true);

  const refresh = async () => {
    setLoading(true);
    // setPoints([]);

    // TODO: use Promise.all

    const stops = await getStops();

    const meeting = await getMeetingDetails(meetingUuid, userUuid);

    const stopNames = getMeetingMembersStopNames(meeting);

    const locations = await getStopsByNames(stopNames, stops);
    setLocations(locations);

    const query = { startStopNames: stopNames, metric };
    const points = await findMeetingPoints(query);
    setPoints(points);

    setLoading(false);
  };

  React.useEffect(() => {
    refresh();
  }, [metric]);

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

  const handleSelect = (stop) => {
    console.log(stop.name);

    navigation.pop();
  };

  return (
    <View style={{ height: "100%" }}>
      <View style={{ flexDirection: "row" }}>
        {availableMetrics.map(({ name, label }) => (
          <View style={{ flex: 1 }}>
            <Button
              onPress={() => setMetric(name)}
              mode="contained"
              color={name === metric ? "lightgray" : "white"}
              style={{ borderRadius: 0 }}
              textStyle={{ borderRadius: 0 }}
            >
              {label}
            </Button>
          </View>
        ))}
      </View>
      <Divider />
      <View style={{ flex: 1 }}>
        <MapView
          ref={mapRef}
          loadingEnabled={true}
          initialRegion={initialRegion}
          maxZoomLevel={18}
          moveOnMarkerPress={false}
          style={{ height: "100%" }}
          // opacity={loading ? 0.6 : 1}
        >
          {locations.map((location, i) => (
            <Marker
              key={"location-" + i}
              coordinate={location}
              pinColor="red"
              onPress={() => handleSelect(location)}
              zIndex={2}
            />
          ))}
          {points.map((point, i) => (
            <Marker
              key={"point-" + i}
              coordinate={point}
              pinColor="green"
              onPress={() => handleSelect(point)}
              zIndex={1}
            />
          ))}
        </MapView>
      </View>
    </View>
  );
}
