using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FlashDisplay : MonoBehaviour
{
    public float delay;
    float countdown = 0;

    // Start is called before the first frame update
    void Start() {
        gameObject.SetActive(false);
    }

    public void Begin()
    {
        gameObject.SetActive(true);
        countdown = delay;
    }

    public void End() {
        gameObject.SetActive(false);
        countdown = 0;
    }

    // Update is called once per frame
    void Update()
    {
        countdown -= Time.deltaTime;
        if (countdown <= 0) {
            End();
        }
    }
}
