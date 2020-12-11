import * as React from "react";
import { View } from "react-native";
import { List, RadioButton } from "react-native-paper";
import { censorUuid } from "../utils";

export default function SelectAccount({
  users = [],
  selected = null,
  onChange = () => {},
  color = null,
  style = {},
}) {
  return (
    <View style={style}>
      <RadioButton.Group value={selected}>
        {users.map(({ uuid, nickname }) => (
          <List.Item
            key={uuid}
            onPress={() => onChange(uuid)}
            title={nickname === null ? "Tożsamość bez nazwy" : nickname}
            titleStyle={nickname === null ? { opacity: 0.2 } : null}
            description={censorUuid(uuid)}
            left={(props) => (
              <View style={{ marginTop: 8 }}>
                <RadioButton {...props} value={uuid} color={color} />
              </View>
            )}
          />
        ))}
      </RadioButton.Group>
    </View>
  );
}
