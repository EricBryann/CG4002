using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Grenade : MonoBehaviour
{

    public float delay = 2f;
    public GameObject explosionEffect;
    float countdown;

    void Explode() {
        Instantiate(explosionEffect, transform.position, transform.rotation);
    }

    // Start is called before the first frame update
    void Start()
    {
        countdown = delay;
    }

    // Update is called once per frame
    void Update()
    {
        countdown -= Time.deltaTime;
        if (countdown <= 0) {
            if (explosionEffect) {
                Explode();
            }
            // Code to detect and decrease HP of other player.
            Destroy(gameObject);
        }
    }
}
