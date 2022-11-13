using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerStats
{
    public int hp;
	public string action;
	public int bullets;
	public int grenades;
	public int shield_time;
    public int shield_health;
    public int num_deaths;
	public int num_shield;

    public static PlayerStats GetJSON(string jsonString) {
        return JsonUtility.FromJson<PlayerStats>(jsonString);
    }
}
