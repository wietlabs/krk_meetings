import * as React from "react";
import { Alert, View } from "react-native";
import { FAB } from "react-native-paper";
import { findOptimalSequence } from "../../api/ConnectionsApi";
import StopsInputList from "../../components/StopsInputList";

export default function FindSequenceScreen({ navigation }) {
  const [stops, setStops] = React.useState([""]);
  const [loading, setLoading] = React.useState(false);

  const showError = (message) => {
    Alert.alert("Wystąpił błąd", message);
  };

  const handleSubmit = async () => {
    if (stops.length < 2) {
      showError("Proszę wybrać co najmniej 3 przystanki");
      return;
    }

    if (stops.length == 2) {
      const [startStopName, endStopName] = stops;
      navigation.navigate("ConnectionsStack", {
        screen: "FindConnections",
        params: { startStopName, endStopName },
      });
      return;
    }

    setLoading(true);
    const startStopName = stops[0];
    const stopsToVisit = stops.slice(1, -1);
    const endStopName = stops[stops.length - 1];
    const query = { startStopName, stopsToVisit, endStopName };
    try {
      const sequence = await findOptimalSequence(query);
      navigation.navigate("SequenceResult", { sequence });
    } catch (e) {
      const error = e.response.data.error;
      if (error === "BAD START STOP NAME") {
        showError("Nie znaleziono przystanku początkowego");
      } else if (error === "BAD STOP NAME IN REQUESTED SEQUENCE") {
        showError("Nie znaleziono przystanku pośredniego");
      } else if (error === "BAD END STOP NAME") {
        showError("Nie znaleziono przystanku końcowego");
      } else {
        showError(error);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1 }}>
      <StopsInputList
        stops={stops}
        setStops={setStops}
        min={1}
        max={8}
        disabled={loading}
      />
      <FAB
        icon={"auto-fix"}
        onPress={handleSubmit}
        loading={loading}
        style={{
          position: "absolute",
          margin: 16,
          right: 0,
          bottom: 0,
          backgroundColor: "khaki",
          zIndex: 10,
        }}
      />
    </View>
  );
}
