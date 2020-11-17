import * as React from "react";
import { View, ScrollView } from "react-native";
import MapView, { Marker } from "react-native-maps";
import { Button, Divider, List, ProgressBar } from "react-native-paper";
import { getStops, findMeetingPoints } from "../../api/ConnectionsApi";
import {
  getMeetingDetails,
  updateMeetingStopName,
} from "../../api/MeetingsApi";
import { getMeetingMembersStopNames, getStopsByNames } from "../../utils";

const initialRegion = {
  latitude: 50.04,
  longitude: 19.96,
  latitudeDelta: 0.3,
  longitudeDelta: 0.4,
};

const padding = {
  top: 150,
  bottom: 50,
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

  const [metric, setMetric] = React.useState("square");
  const [locations, setLocations] = React.useState([]);
  const [points, setPoints] = React.useState([]);
  const [selected, setSelected] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  const refresh = async () => {
    setLoading(true);
    // setPoints([]);

    // TODO: use Promise.all

    const stops = await getStops();

    const meeting = await getMeetingDetails(meetingUuid, userUuid);
    setSelected({ name: meeting?.stop_name });

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

  const handlePress = (stop) => {
    if (stop.name === selected?.name) handleSubmit(stop);
    else handleSelect(stop);
  };

  const handleSelect = (stop) => {
    setSelected(stop);
  };

  const handleSubmit = async (stop) => {
    await updateMeetingStopName(meetingUuid, userUuid, stop.name);
    navigation.pop();
  };

  const maxMetricValue = Math.max(...points.map((point) => point.metric));

  return (
    <View style={{ height: "100%" }}>
      <View style={{ flexDirection: "row" }}>
        {availableMetrics.map(({ name, label }) => (
          <View key={name} style={{ flex: 1 }}>
            <Button
              onPress={() => setMetric(name)}
              mode="contained"
              color={name === metric ? "lightgray" : "white"}
              style={{ borderRadius: 0 }}
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
          style={{ flex: 1 }}
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
          {points.map((point, i) => {
            const isSelected = point.name === selected?.name;
            return (
              <Marker
                key={"point-" + i + (isSelected ? "-selected" : "")}
                coordinate={point}
                pinColor={isSelected ? "green" : "yellow"}
                onPress={() => handlePress(point)}
                zIndex={isSelected ? 3 : 1}
              />
            );
          })}
        </MapView>
      </View>
      <Divider />
      <ScrollView style={{ flex: 1 }}>
        {points.map((point, i) => {
          const isSelected = point.name === selected?.name;
          return (
            <React.Fragment key={i}>
              <List.Item
                title={point.name}
                // description={() => (
                //   <ProgressBar
                //     progress={point.metric / maxMetricValue}
                //     style={{ marginTop: 2 }}
                //   />
                // )}
                // description={point.metric}
                left={(props) => (
                  <List.Icon
                    {...props}
                    icon={"map-marker"}
                    style={{ margin: 0 }}
                  />
                )}
                style={{ backgroundColor: "white" }}
                titleStyle={isSelected && { fontWeight: "bold" }}
                onPress={() => handlePress(point)}
              />
              <Divider />
            </React.Fragment>
          );
        })}
      </ScrollView>
    </View>
  );
}
