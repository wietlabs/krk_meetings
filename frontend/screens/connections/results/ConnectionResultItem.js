import * as React from "react";
import { View } from "react-native";
import { Card, Text } from "react-native-paper";
import RouteButton from "./RouteChip";
import WalkButton from "./WalkChip";
import DelayText from "../../../components/DelayText";
import {
  parseDateTime,
  formatTime,
  addMinutes,
  filterTransfers,
} from "../../../utils";

function HourDelayStop({ time, delay, stop }) {
  return (
    <View style={{ flexDirection: "row" }}>
      <Text style={{ fontWeight: "bold" }}>{formatTime(time)}</Text>
      <DelayText delay={delay} />
      <Text style={{ position: "absolute", left: 50 }}>{stop}</Text>
    </View>
  );
}

export default function ConnectionResultItem({ connection, onPress }) {
  const actions = connection.actions;
  const transfers = filterTransfers(actions);

  let startDateTime,
    endDateTime,
    startDelay,
    endDelay,
    startStopName,
    endStopName;

  if (connection.walking_only) {
    const action = actions[0];
    startDateTime = new Date();
    endDateTime = addMinutes(startDateTime, action.duration_in_minutes);
    startDelay = null;
    endDelay = null;
    startStopName = action.start_stop_name;
    endStopName = action.end_stop_name;
  } else {
    const first_transfer = transfers[0];
    const last_transfer = transfers[transfers.length - 1];
    startDateTime = parseDateTime(first_transfer.start_datetime);
    endDateTime = parseDateTime(last_transfer.end_datetime);
    startDelay = first_transfer.delay;
    endDelay = first_transfer.delay;
    startStopName = first_transfer.start_stop_name;
    endStopName = last_transfer.end_stop_name;
  }

  return (
    <Card onPress={onPress} style={{ marginTop: 12, marginBottom: 16 }}>
      <Card.Content
        style={{
          flex: 1,
          flexDirection: "row",
          marginTop: -30,
          marginBottom: 6,
        }}
      >
        {actions.map((action, i) => {
          switch (action.type) {
            case "transfer":
              return (
                <RouteButton routeName={action.route_name} key={i} nth={i} />
              );
            case "walking":
              return (
                <WalkButton duration={action.duration_in_minutes} key={i} />
              );
          }
        })}
      </Card.Content>
      <Card.Content>
        <HourDelayStop
          time={startDateTime}
          delay={startDelay}
          stop={startStopName}
        />
        <HourDelayStop time={endDateTime} delay={endDelay} stop={endStopName} />
      </Card.Content>
    </Card>
  );
}
