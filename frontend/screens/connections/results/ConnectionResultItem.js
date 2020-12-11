import * as React from "react";
import { View } from "react-native";
import { Card, Text } from "react-native-paper";
import RouteButton from "./RouteChip";
import WalkButton from "./WalkChip";
import DelayText from "../../../components/DelayText";
import { parseDateTime, formatTime, filterTransfers } from "../../../utils";

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

  const startStopName = connection.start_stop_name;
  const endStopName = connection.end_stop_name;
  const startDateTime = parseDateTime(connection.start_datetime);
  const endDateTime = parseDateTime(connection.end_datetime);

  let startDelay, endDelay;
  if (connection.walking_only) {
    startDelay = endDelay = null;
  } else {
    const transfers = filterTransfers(actions);
    const first_transfer = transfers[0];
    const last_transfer = transfers[transfers.length - 1];
    startDelay = first_transfer.delay;
    endDelay = last_transfer.delay;
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
