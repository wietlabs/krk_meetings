import * as React from "react";
import { Alert, Keyboard, View } from "react-native";
import { Button, IconButton, TextInput, FAB } from "react-native-paper";
import DateTimePicker from "@react-native-community/datetimepicker";
import { findConnections } from "../../../api/ConnectionsApi";
import { makeDateTime } from "../../../utils";
import NearestStopsMap from "../../../components/NearestStopsMap";

const initialState = {
  startStopName: "Czerwone Maki P+R",
  endStopName: "Czarnowiejska",
  date: null,
  time: null,
  mode: null,
  show: false,
  mapVisible: false,
};

const ACTIONS = {
  SET_START_END_STOP_NAME: "set-start-end-stop-name",
  SET_START_STOP_NAME: "set-start-stop-name",
  SET_END_STOP_NAME: "set-end-stop-name",
  CLEAR_START_STOP_NAME: "clear-start-stop-name",
  CLEAR_END_STOP_NAME: "clear-end-stop-name",
  SWAP_STOP_NAMES: "swap-stop-names",
  SHOW_MAP: "show-map",
  HIDE_MAP: "hide-map",
  SELECT_START_STOP: "select-start-stop",
  PICK_DATE: "pick-date",
  PICK_TIME: "pick-time",
  SET_DATE: "set-date",
  SET_TIME: "set-time",
  CANCEL: "cancel",
  CLEAR_DATE: "clear-date",
  CLEAR_TIME: "clear-time",
};

export default function HomeScreen({ navigation, route }) {
  const startStopNameRef = React.useRef();
  const endStopNameRef = React.useRef();

  const reducer = (state, action) => {
    switch (action.type) {
      case ACTIONS.SET_START_END_STOP_NAME:
        return {
          ...state,
          startStopName: action.payload.startStopName,
          endStopName: action.payload.endStopName,
        };

      case ACTIONS.SET_START_STOP_NAME:
        return { ...state, startStopName: action.payload.startStopName };

      case ACTIONS.SET_END_STOP_NAME:
        return { ...state, endStopName: action.payload.endStopName };

      case ACTIONS.CLEAR_START_STOP_NAME:
        return { ...state, startStopName: "" };

      case ACTIONS.CLEAR_END_STOP_NAME:
        return { ...state, endStopName: "" };

      case ACTIONS.SWAP_STOP_NAMES:
        return {
          ...state,
          startStopName: state.endStopName,
          endStopName: state.startStopName,
        };

      case ACTIONS.SHOW_MAP:
        Keyboard.dismiss();
        return { ...state, mapVisible: true };

      case ACTIONS.HIDE_MAP:
        startStopNameRef.current.focus();
        return { ...state, mapVisible: false };

      case ACTIONS.SELECT_START_STOP:
        endStopNameRef.current.focus();
        return {
          ...state,
          startStopName: action.payload.startStopName,
          mapVisible: false,
        };

      case ACTIONS.PICK_DATE:
        return { ...state, mode: "date", show: true };

      case ACTIONS.PICK_TIME:
        return { ...state, mode: "time", show: true };

      case ACTIONS.CLEAR_DATE:
        return { ...state, date: null, time: null };

      case ACTIONS.CLEAR_TIME:
        return { ...state, time: null };

      case ACTIONS.CANCEL:
        return { ...state, show: false };

      case ACTIONS.SET_DATE:
        return { ...state, date: action.payload.date, mode: "time" };

      case ACTIONS.SET_TIME:
        return { ...state, time: action.payload.time, show: false };

      default:
        return state;
    }
  };

  const [state, dispatch] = React.useReducer(reducer, initialState);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (route.params?.startStopName && route.params?.endStopName) {
      dispatch({
        type: ACTIONS.SET_START_END_STOP_NAME,
        payload: { ...route.params },
      });
    }
  }, [route.params]);

  const handleChangeStartStopName = (startStopName) => {
    dispatch({ type: ACTIONS.SET_START_STOP_NAME, payload: { startStopName } });
  };

  const handleChangeEndStopName = (endStopName) => {
    dispatch({ type: ACTIONS.SET_END_STOP_NAME, payload: { endStopName } });
  };

  const handleSelectStartStop = (stop) => {
    dispatch({
      type: ACTIONS.SELECT_START_STOP,
      payload: { startStopName: stop.name },
    });
  };

  const handlePickDate = () => {
    dispatch({ type: ACTIONS.PICK_DATE });
  };

  const handlePickTime = () => {
    dispatch({ type: ACTIONS.PICK_TIME });
  };

  const handleClearDate = () => {
    dispatch({ type: ACTIONS.CLEAR_DATE });
  };

  const handleClearTime = () => {
    dispatch({ type: ACTIONS.CLEAR_TIME });
  };

  const handlePick = (event, value) => {
    if (event.type === "dismissed") {
      dispatch({ type: ACTIONS.CANCEL });
      return;
    }
    if (mode === "date") {
      dispatch({ type: ACTIONS.SET_DATE, payload: { date: value } });
      return;
    }
    if (mode === "time") {
      dispatch({ type: ACTIONS.SET_TIME, payload: { time: value } });
      return;
    }
  };

  const {
    startStopName,
    endStopName,
    date,
    time,
    show,
    mode,
    mapVisible,
  } = state;

  const handleSubmit = async () => {
    setLoading(true);
    const now = new Date();
    const startDateTime = makeDateTime(date || now, time || now);
    const query = { startDateTime, startStopName, endStopName };
    try {
      const connections = await findConnections(query);
      navigation.navigate("ConnectionResults", {
        startDateTime: startDateTime.getTime(),
        connections,
      });
    } catch (e) {
      const error = e.response.data.error;
      if (error === "BAD START STOP NAME") {
        showError("Nie znaleziono przystanku początkowego");
      } else if (error === "BAD END STOP NAME") {
        showError("Nie znaleziono przystanku końcowego");
      } else if (error === "BAD QUERY ID VALUE") {
        showError("Prosimy spróbować ponownie");
      } else {
        showError(error);
      }
    }
    setLoading(false);
  };

  const showError = (message) => {
    Alert.alert("Wystąpił błąd", message);
  };

  const now = new Date();

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <TextInput
        ref={startStopNameRef}
        value={startStopName}
        label="Przystanek początkowy"
        left={
          <TextInput.Icon
            name="map-marker-radius"
            onPress={() => dispatch({ type: ACTIONS.SHOW_MAP })}
          />
        }
        right={
          <TextInput.Icon
            name="close"
            onPress={() => dispatch({ type: ACTIONS.CLEAR_START_STOP_NAME })}
          />
        }
        onChangeText={handleChangeStartStopName}
        style={{ backgroundColor: "white" }}
      />
      <View style={{ alignItems: "center" }}>
        <IconButton
          icon="cached"
          onPress={() => dispatch({ type: ACTIONS.SWAP_STOP_NAMES })}
        />
      </View>
      <TextInput
        ref={endStopNameRef}
        value={endStopName}
        label="Przystanek końcowy"
        left={<TextInput.Icon name="flag-checkered" />}
        right={
          <TextInput.Icon
            name="close"
            onPress={() => dispatch({ type: ACTIONS.CLEAR_END_STOP_NAME })}
          />
        }
        onChangeText={handleChangeEndStopName}
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
          onPress={date === null ? handlePickDate : handleClearDate}
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
          onPress={time === null ? handlePickTime : handleClearTime}
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
        visible={!mapVisible}
        onPress={handleSubmit}
        style={{
          position: "absolute",
          margin: 16,
          right: 0,
          bottom: 0,
          backgroundColor: "springgreen",
          zIndex: 10,
        }}
      />
      {show && (
        <DateTimePicker
          mode={mode}
          is24Hour={true}
          minimumDate={now}
          value={(mode === "date" ? date : time) || now}
          onChange={handlePick}
        />
      )}
      {mapVisible && (
        <NearestStopsMap
          onSelect={handleSelectStartStop}
          onClose={() => dispatch({ type: ACTIONS.HIDE_MAP })}
        />
      )}
    </View>
  );
}
