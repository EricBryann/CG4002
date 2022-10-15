using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Opponent : MonoBehaviour
{
    
    public Text displayHealth;
    public int healthValue;

    public GameObject opponentInFrame;

    public FlashDisplay shieldPrefab;
    public Text currentOppShields;
    public int shieldCount;
    public int shieldHealth = 0;

    public Text currentOppGrenades;
    public int grenadeCount;
    
    public Text currentOppBullets;
    public int bulletCount;

    public Text killCountDisplay;
    public int killCount;

    /**
        Opponent AR Marker Detection
    **/

    public bool isOpponentDetected = false;

	public void SetOpponentDetected(bool isDetected) {
		isOpponentDetected = isDetected;
        opponentInFrame.SetActive(isDetected);
		if (isDetected) {
            Debug.Log("Opponent Detected!");
        } else {
            Debug.Log("Opponent Not Detected!");
        }
	}

	public bool GetIsOpponentDetected() {
        // Debug.Log(isOpponentDetected.ToString());
        return isOpponentDetected;
    }

    /**
        Opponent Shield Count and Detection
    **/

    public void UpdateOppShieldCount(int nShields) {
        shieldCount = nShields;
        currentOppShields.text = shieldCount.ToString();
    }

    public void ActivateShield() {
        shieldPrefab.Begin();
    }

    public void DeactivateShield() {
        shieldPrefab.End();
    }

    // public void DecreaseShieldHealth(int damage) {
    //     if (shieldHealth >= 0) {
    //         shieldHealth -= damage;
    //     }
    // }

    /**
        Opponent health stuff
    **/

    public void UpdateOppHealth(int health) {
        displayHealth.text = health.ToString();
    }

    // public void GiveDamage(int damage) {
    //     if (healthValue > 0) {
    //         healthValue -= damage;
    //         if (healthValue <= 0) {
    //             IncreaseKillCount();
    //         }
    //         DecreaseShieldHealth(damage);
    //         UpdateOppHealth(healthValue);
    //     }
    //     if (damage == 30 || shieldHealth <= 0) {
    //         DeactivateShield();
    //     }
	// }

    public int GetOppCurrentHP() {
        return healthValue;
    }

    /**
        Opponent grenade count
    **/

    public void UpdateOppGrenadeCount(int nGrenades) {
        grenadeCount = nGrenades;
        currentOppGrenades.text = grenadeCount.ToString();
    }

    /**
        Opponent bullet count
    **/

    public void UpdateOppBulletCount(int nBullets) {
        bulletCount = nBullets;
        currentOppBullets.text = bulletCount.ToString();
    }

}
