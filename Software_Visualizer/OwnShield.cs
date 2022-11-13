using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class OwnShield : MonoBehaviour
{
    public FlashDisplay ownShieldPrefab;
    public int shieldCount;
    public Text currentShields;
    public int currentShieldHealth = 0;

    public void SetShieldCount(int nShields) {
        shieldCount = nShields;
        currentShields.text = nShields.ToString();
    }

    public void UpdateShieldCount(int nShields) {
        shieldCount = nShields;
        currentShields.text = shieldCount.ToString();
    }

    public void ActivateOwnShield() {
        ownShieldPrefab.Begin();
    }

    public void DeactivateOwnShield() {
        ownShieldPrefab.End();
    }

    public void DecreaseShieldHealth(int damage) {
        if (currentShieldHealth >= 0) {
            currentShieldHealth -= damage;
        } 
    }

    public int GetCurrentShieldHealth() {
        return currentShieldHealth;
    }

    // Returns the current no of shields
    public int GetCurrentShieldCount() {
        return shieldCount;
    }


}
