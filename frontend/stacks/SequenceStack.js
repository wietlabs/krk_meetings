import * as React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import FindSequenceScreen from "../screens/sequence/FindSequenceScreen";
import SequenceResultScreen from "../screens/sequence/SequenceResultScreen";

const Stack = createStackNavigator();

export default function SequenceStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="FindSequence"
        component={FindSequenceScreen}
        options={{ title: "Wyszukiwarka optymalnej sekwencji" }}
      />
      <Stack.Screen
        name="SequenceResult"
        component={SequenceResultScreen}
        options={{ title: "Optymalna sekwencja" }}
      />
    </Stack.Navigator>
  );
}
