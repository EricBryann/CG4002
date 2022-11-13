using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class HealthBar : MonoBehaviour
{
    public Slider slider;
    public Text displayHealth;
    public int hpValue;
    public FlashDisplay tintScreen;
    public FlashDisplay opponentGrenadeIcon;

    public void SetHPValue(int health) {
        hpValue = health;
        slider.maxValue = health;
        slider.value = health;
        displayHealth.text = health.ToString();
    }

    public void UpdateHealth(int health, bool isDecrease, bool isHitByGreande) {
        hpValue = health;
        slider.value = health;
        displayHealth.text = health.ToString();
        if (isDecrease) {
            Handheld.Vibrate();
            tintScreen.Begin();
        }
        if (isHitByGreande) {
            opponentGrenadeIcon.Begin();
        }
    }

    public int GetCurrentHealth() {
        return hpValue;
    }
}
