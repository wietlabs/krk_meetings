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

  let start_datetime,
    end_datetime,
    start_delay,
    end_delay,
    start_stop_name,
    end_stop_name;

  if (connection.walking_only) {
    const action = actions[0];
    start_datetime = new Date();
    end_datetime = addMinutes(start_datetime, connection.duration_in_minutes);
    start_delay = null;
    end_delay = null;
    start_stop_name = action.start_stop_name;
    end_stop_name = action.end_stop_name;
  } else {
    const first_transfer = transfers[0];
    const last_transfer = transfers[transfers.length - 1];
    start_datetime = parseDateTime(first_transfer.start_datetime);
    end_datetime = parseDateTime(last_transfer.end_datetime);
    start_delay = first_transfer.delay;
    end_delay = first_transfer.delay;
    start_stop_name = first_transfer.start_stop_name;
    end_stop_name = last_transfer.end_stop_name;
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
          time={start_datetime}
          delay={start_delay}
          stop={start_stop_name}
        />
        <HourDelayStop
          time={end_datetime}
          delay={end_delay}
          stop={end_stop_name}
        />
      </Card.Content>
    </Card>
  );
}
