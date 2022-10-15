using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Shooter : MonoBehaviour
{
    public int bulletCount;
    public AudioSource firingSound;
    public AudioSource reloadSound;
    public Text currentBullets;

    public void ReloadSound() {
        Instantiate(reloadSound).Play();
    }

    public void UpdateBulletCount(int nBullets) {
        bulletCount = nBullets;
        currentBullets.text = bulletCount.ToString();
    }

    public void Shoot() {
        Handheld.Vibrate();
        Instantiate(firingSound).Play();
    }

    // Returns the current no of bullets
    public int GetCurrentBulletCount() {
        return bulletCount;
    }
}
