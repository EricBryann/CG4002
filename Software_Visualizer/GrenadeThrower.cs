using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GrenadeThrower : MonoBehaviour
{
    public float throwForce = 1000f;
    public GameObject grenadePrefab;
    public int grenadeCount;
    public Text currentGrenades;
    public AudioSource throwSound;

    public void SetGrenadeCount(int nGrenades) {
        grenadeCount = nGrenades;
        currentGrenades.text = nGrenades.ToString();
    }

    public void UpdateGrenadeCount(int nGrenades) {
        grenadeCount = nGrenades;
        currentGrenades.text = grenadeCount.ToString();
    }

    public void ThrowGrenade() {
        GameObject grenade = Instantiate(grenadePrefab, transform.position, transform.rotation);
        Instantiate(throwSound).Play();
        Rigidbody rb = grenade.GetComponent<Rigidbody>();
        rb.AddForce(transform.forward * throwForce, ForceMode.VelocityChange);
    }

    // Returns the current no of grenades
    public int GetCurrentGrenadeCount() {
        return grenadeCount;
    }
}
