using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Score : MonoBehaviour
{
    public Text killCount;
    public Text deathCount;

    public void UpdateKills(int kills) {
        killCount.text = kills.ToString();
    }
    
    public void UpdateDeaths(int nDeath) {
        deathCount.text = nDeath.ToString();
    }
}
