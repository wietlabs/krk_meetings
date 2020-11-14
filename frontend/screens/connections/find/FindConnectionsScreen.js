import * as React from "react";
import { Alert, View } from "react-native";
import { Button, IconButton, TextInput, FAB } from "react-native-paper";
import DateTimePicker from "@react-native-community/datetimepicker";
import { findConnections } from "../../../api/ConnectionsApi";

export default function HomeScreen({ navigation }) {
  const [startStopName, setStartStopName] = React.useState("Czerwone Maki P+R");
  const [endStopName, setEndStopName] = React.useState("Jerzmanowskiego");
  const [loading, setLoading] = React.useState(false);

  const now = new Date();
  const [date, setDate] = React.useState(null);
  const [time, setTime] = React.useState(null);
  const [show, setShow] = React.useState(false);
  const [mode, setMode] = React.useState(null);

  const handleSwap = () => {
    setStartStopName(endStopName);
    setEndStopName(startStopName);
  };

  const handleSelectDate = () => {
    setMode("date");
    setShow(true);
  };

  const handleSelectTime = () => {
    setMode("time");
    setShow(true);
  };

  const handleClearDate = () => {
    setDate(null);
    setTime(null);
  };

  const handleClearTime = () => {
    setTime(null);
  };

  const handlePick = (event, value) => {
    if (event.type === "dismissed") {
      setShow(false);
      return;
    }
    if (mode === "date") {
      setMode("time");
      setDate(value);
      return;
    }
    if (mode === "time") {
      setShow(false);
      setTime(value);
      return;
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    const now = new Date();
    const d = date || now;
    const t = time || now;
    const startDateTime = new Date(
      d.getYear() + 1900,
      d.getMonth(),
      d.getDate(),
      t.getHours(),
      t.getMinutes()
    );
    const query = { startDateTime, startStopName, endStopName };
    try {
      const connections = await findConnections(query);
      navigation.navigate("ConnectionResults", {
        startDateTime: startDateTime.getTime(),
        connections,
      });
    } catch (e) {
      Alert.alert(
        "Wystąpił błąd",
        "Wystąpił błąd podczas wyszukiwania połączenia."
      );
    }
    setLoading(false);
  };

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <TextInput
        value={startStopName}
        label="Przystanek początkowy"
        left={<TextInput.Icon name="map-marker-radius" />}
        right={
          <TextInput.Icon name="close" onPress={() => setStartStopName("")} />
        }
        onChangeText={setStartStopName}
        style={{ backgroundColor: "white" }}
      />
      <View style={{ alignItems: "center" }}>
        <IconButton icon="cached" onPress={handleSwap} />
      </View>
      <TextInput
        value={endStopName}
        label="Przystanek końcowy"
        left={<TextInput.Icon name="flag-checkered" />}
        right={
          <TextInput.Icon name="close" onPress={() => setEndStopName("")} />
        }
        onChangeText={setEndStopName}
        style={{ backgroundColor: "white", marginBottom: 16 }}
      />
      <View
        style={{
          flexDirection: "row",
          alignContent: "center",
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <Button
          mode="outlined"
          onPress={date === null ? handleSelectDate : handleClearDate}
          color={date === null ? "lightgray" : "black"}
          style={{
            flex: 0.5,
            borderColor: date === null ? "lightgray" : "black",
          }}
        >
          {date === null
            ? "Dzisiaj"
            : [date.getDate(), date.getMonth(), date.getYear() + 1900].join(
                "."
              )}
        </Button>
        <View style={{ width: 16 }}></View>
        <Button
          mode="outlined"
          onLongPress={handleClearTime}
          onPress={time === null ? handleSelectTime : handleClearTime}
          color={time === null ? "lightgray" : "black"}
          style={{
            flex: 0.5,
            borderColor: time === null ? "lightgray" : "black",
          }}
        >
          {time === null ? "Teraz" : time.toLocaleTimeString().slice(0, 5)}
        </Button>
      </View>
      <FAB
        icon={"magnify"}
        loading={loading}
        disabled={loading}
        onPress={handleSubmit}
        style={{
          position: "absolute",
          margin: 16,
          right: 0,
          bottom: 0,
          backgroundColor: "springgreen",
        }}
      />
      {show && (
        <DateTimePicker
          mode={mode}
          value={(mode === "date" ? date : time) || now}
          onChange={handlePick}
        />
      )}
    </View>
  );
}
