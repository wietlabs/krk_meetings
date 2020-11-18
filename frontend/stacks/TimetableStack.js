import * as React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import TimetableScreen from "../screens/timetable/TimetableScreen";

const Stack = createStackNavigator();

export default function TimetableStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="Timetable"
        component={TimetableScreen}
        options={{ title: "Rozkłady jazdy" }}
      />
    </Stack.Navigator>
  );
}
