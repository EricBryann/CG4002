using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

using M2MqttUnity;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;
using SimpleJSON;

public class Player : M2MqttUnityClient
{

    public const string CURRENT_PLAYER = "p1";
    public const string OPPONENT_PLAYER = "p2";

	public int maxHealth = 100;
	public int maxShields = 3;
	public int maxGrenades = 2;
	public int maxBullets = 6;
	
	public int currentHealth;
	public int currentOppHealth;
	public int currentGrenadeCount;

	public HealthBar healthBar;
	public GrenadeThrower grenadeThrowing;
	public Opponent opponent;
	public OwnShield ownShield;
	public Shooter fps;
    public Score scores;
    public GameOver over;

	public int newMyHP;
    public string newMyAction;
    public int newMyBullets;
	public int newMyGrenades;
	public int newMyKills;
	public int newMyShields;
    public int myShieldHealth;
    public int myShieldTime;
	
	public int newOppHP;
    public string newOppAction;
    public int newOppBullets;
	public int newOppGrenades;
	public int newOppKills;
	public int newOppShields;
    public int oppShieldHealth;
    public int oppShieldTime;

    public string first_msg;

    public Text actionText;

	// MQTT stuff

	public string topicSubscribe = "Capstone/Ultra96Send";
    public string topicPublish = "Capstone/VisualizerReply";
    public string messageToPublish = "";

    public bool autoTest = false;

    private string m_msg;

    // public Text recvdData;

    public string prevsMsg = "";
	public string msg
    {
        get
        {
            return m_msg;
        }
        set
        {
            if (m_msg == value) return;
            m_msg = value;
            if (OnMessageArrived != null)
            {
                OnMessageArrived(m_msg);
            }
        }
    }

    public event OnMessageArrivedDelegate OnMessageArrived;
    public delegate void OnMessageArrivedDelegate(string newMsg);

    private bool m_isConnected;

    public bool isConnected
    {
        get
        {
            return m_isConnected;
        }
        set
        {
            if (m_isConnected == value) return;
            m_isConnected = value;
            if (OnConnectionSucceeded != null)
            {
                OnConnectionSucceeded(isConnected);
            }
        }
    }
    public event OnConnectionSucceededDelegate OnConnectionSucceeded;
    public delegate void OnConnectionSucceededDelegate(bool isConnected);

    private List<string> eventMessages = new List<string>();

    /*public void Publish()
    {
        client.Publish(topicPublish, System.Text.Encoding.UTF8.GetBytes(messageToPublish), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
        Debug.Log("Test message published.");
    }*/

    public void SetEncrypted(bool isEncrypted)
    {
        this.isEncrypted = isEncrypted;
    }

    protected override void OnConnecting()
    {
        base.OnConnecting();
    }

    protected override void OnConnected()
    {
        base.OnConnected();
        isConnected = true;

        /*if (autoTest)
        {
            Publish();
        }*/
    }

    protected override void OnConnectionFailed(string errorMessage)
    {
        Debug.Log("CONNECTION FAILED!" + errorMessage);
    }

    protected override void OnDisconnected()
    {
        Debug.Log("Disconnected!");
        isConnected = false;
    }

    protected override void OnConnectionLost()
    {
        Debug.Log("CONNECTION LOST!");
    }

    protected override void SubscribeTopics()
    {
        client.Subscribe(new string[] { topicSubscribe }, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
    }

    protected override void UnsubscribeTopics()
    {
        client.Unsubscribe(new string[] { topicSubscribe });
    }

    // protected override void Start()
    // {
    //     base.Start();
    // }

    protected override void DecodeMessage(string topic, byte[] message)
    {
        msg = System.Text.Encoding.UTF8.GetString(message);

        Debug.Log("Received: " + msg);
        if ((CURRENT_PLAYER == "p1" && msg != "g1") || (CURRENT_PLAYER == "p2" && msg != "g2")) {
            if (msg != "g1" && msg != "g2" && msg != "n1" && msg != "n2") {
                var dataDict = JSON.Parse(msg);

                newMyHP = dataDict[CURRENT_PLAYER]["hp"];
                newMyAction = dataDict[CURRENT_PLAYER]["action"];
                newMyBullets = dataDict[CURRENT_PLAYER]["bullets"];
                newMyGrenades = dataDict[CURRENT_PLAYER]["grenades"];
                newMyKills = dataDict[OPPONENT_PLAYER]["num_deaths"];
                newMyShields = dataDict[CURRENT_PLAYER]["num_shield"];
                myShieldHealth = dataDict[CURRENT_PLAYER]["shield_health"];
                myShieldTime = dataDict[CURRENT_PLAYER]["shield_time"];
                
                newOppHP = dataDict[OPPONENT_PLAYER]["hp"];
                newOppAction = dataDict[OPPONENT_PLAYER]["action"];
                newOppBullets = dataDict[OPPONENT_PLAYER]["bullets"];
                newOppGrenades = dataDict[OPPONENT_PLAYER]["grenades"];
                newOppKills = dataDict[CURRENT_PLAYER]["num_deaths"];
                newOppShields = dataDict[OPPONENT_PLAYER]["num_shield"];
                oppShieldHealth = dataDict[OPPONENT_PLAYER]["shield_health"];
                oppShieldTime = dataDict[OPPONENT_PLAYER]["shield_time"];
            }
        } else {
            ThrowGrenadeAndCheckHit();
        }

        StoreMessage(msg);

        // if (newMyAction == "grenade")
        // {
        //     client.Publish(topicPublish, System.Text.Encoding.UTF8.GetBytes("t"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
        //     Debug.Log("Sent g");
        // }

        if (topic == "")
        {
            if (autoTest)
            {
                autoTest = false;
                Disconnect();
            }
        }
    }

    private void StoreMessage(string eventMsg)
    {
        if (eventMessages.Count > 50)
        {
            eventMessages.Clear();
        }
        eventMessages.Add(eventMsg);
    }

    // protected override void Update()
    // {
    //     base.Update();
    // }

    private void OnDestroy()
    {
        Disconnect();
    }

    private void OnValidate()
    {
        if (autoTest)
        {
            autoConnect = true;
        }
    }

    // Start is called before the first frame update
    protected override void Start()
    {
		base.Start();

		healthBar.SetHPValue(maxHealth);
		grenadeThrowing.SetGrenadeCount(maxGrenades);
		ownShield.SetShieldCount(maxShields);
		fps.ReloadSound();
        fps.UpdateBulletCount(maxBullets);

		opponent.UpdateOppHealth(maxHealth);
		opponent.UpdateOppShieldCount(maxShields);
		opponent.UpdateOppGrenadeCount(maxGrenades);
        opponent.UpdateOppBulletCount(maxBullets);

        first_msg = msg;
        actionText.text = "";
    }

    // Update is called once per frame
    protected override void Update()
    {
        bool ownHealthChangeBool;
		base.Update();

        // Debug.Log("msg: " + msg);
		
		if (msg != first_msg && prevsMsg != msg && msg != "g1" && msg != "g2" && msg != "n1" && msg != "n2") {

			currentHealth = healthBar.GetCurrentHealth();
			currentOppHealth = opponent.GetOppCurrentHP();

			int ownHealthChange = currentHealth - newMyHP;
            if (ownHealthChange > 0) {
                ownHealthChangeBool = true;
            } else {
                ownHealthChangeBool = false;
            }
			int oppHealthChange = currentOppHealth - newOppHP;

            // Own Player inventory
            if (newOppAction == "grenade" && ownHealthChange >= 30) {
                healthBar.UpdateHealth(newMyHP, ownHealthChangeBool, true);
            } else {
                healthBar.UpdateHealth(newMyHP, ownHealthChangeBool, false);
            }
            fps.UpdateBulletCount(newMyBullets);
            grenadeThrowing.UpdateGrenadeCount(newMyGrenades);
            ownShield.UpdateShieldCount(newMyShields);
            scores.UpdateKills(newMyKills);
            scores.UpdateDeaths(newOppKills);

            // Own Player actions
            if (newMyAction == "shield" && myShieldHealth > 0 && myShieldTime > 0) {
                ownShield.ActivateOwnShield();
            }
            if (myShieldHealth <= 0 && myShieldTime <= 0 || newMyHP <= 0) {
                ownShield.DeactivateOwnShield();
            }

            // if (newMyAction == "grenade" && newMyGrenades >= 0) {
            //     ThrowGrenadeAndCheckHit();
            // }

            if (newMyAction == "reload") {
                fps.ReloadSound();
            }

            if (newMyAction == "shoot") {
                fps.Shoot();
            }

            // Opp Player inventory
            opponent.UpdateOppHealth(newOppHP);
            opponent.UpdateOppBulletCount(newOppBullets);
            opponent.UpdateOppGrenadeCount(newOppGrenades);
            opponent.UpdateOppShieldCount(newOppShields);

            if (newOppAction == "shield" && oppShieldHealth > 0 && oppShieldTime > 0) {
                opponent.ActivateShield();
            }
            if (oppShieldHealth <= 0 && oppShieldTime <= 0 || newOppHP <= 0) {
                opponent.DeactivateShield();
            }

            if (newMyAction == "logout") {
                over.Display();
            }

            actionText.text = "";

			
			// Rebirth
			// if (currentHealth <= 0) {
			// 	ownShield.DeactivateOwnShield();

			// 	currentHealth = maxHealth;
			// 	healthBar.SetHPValue(maxHealth);
			// 	grenadeThrowing.SetGrenadeCount(maxGrenades);
			// 	ownShield.SetShieldCount(maxShields);
			// 	fps.Reload(maxBullets);
			// }
			// // Opponent is dead
			// if (currentOppHealth <= 0) {
			// 	opponent.DeactivateShield();
			// }
			// // If shot, -10 HP
			// if (newOppAction == "shoot" && ownHealthChange >= 10)
			// {
			// 	PlayerShot();
			// }
			// // If hit by grenade, -30 HP
			// if (newOppAction == "grenade" && ownHealthChange >= 30)
			// {
			// 	PlayerHitByGrenade();
			// }
			// // Throw max 2 grenades per life
			// if (newMyAction == "grenade") {
			// 	ThrowGrenadeAndCheckHit();
			// }
			// // Activate shield on opponent
			// if (newOppAction == "shield") {
			// 	opponent.ActivateShield();
			// }
			// // Opponent hit by bullet
			// if (newMyAction == "shoot" && oppHealthChange == 10) {
			// 	opponent.GiveDamage(10);
			// }
			// // Activate own shield
			// if (newMyAction == "shield") {
			// 	ownShield.ActivateOwnShield();
			// }
			// // Shoot bullet
			// if (newMyAction == "shoot") {
			// 	fps.Shoot();
			// }
			// // Reload magazine
			// if (newMyAction == "reload") {
			// 	fps.Reload(maxBullets);
			// }

			prevsMsg = msg;

		} else if (CURRENT_PLAYER == "p1" && msg == "n1" || CURRENT_PLAYER == "p2" && msg == "n2") {
            actionText.text = "None";
			prevsMsg = msg;
        } else {
            actionText.text = "";
        }

	}

	public void ThrowGrenadeAndCheckHit() {
		grenadeThrowing.ThrowGrenade();
		if (opponent.GetIsOpponentDetected() && CURRENT_PLAYER == "p1") {
            client.Publish(topicPublish, System.Text.Encoding.UTF8.GetBytes("t1"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Just published grenade t1.");
		} else if (opponent.GetIsOpponentDetected() && CURRENT_PLAYER == "p2") {
            client.Publish(topicPublish, System.Text.Encoding.UTF8.GetBytes("t2"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Just published grenade t2.");
		} else if (!opponent.GetIsOpponentDetected() && CURRENT_PLAYER == "p1") {
            client.Publish(topicPublish, System.Text.Encoding.UTF8.GetBytes("f1"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Just published grenade f1.");
        } else {
            client.Publish(topicPublish, System.Text.Encoding.UTF8.GetBytes("f2"), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);
            Debug.Log("Just published grenade f2.");
        }
	}

	public void PlayerHitByGrenade() {
		// healthBar.TakeDamage(30);
		// healthBar.UpdateHealth(newMyHP);
		ownShield.DecreaseShieldHealth(30);
		ownShield.DeactivateOwnShield();
		// opponent.UpdateOppGrenadeCount();
	}
	
	// public void Revive() {
	// 	opponent.SetOppHP(maxHealth);
	// 	opponent.SetOppShields(maxShields);
	// 	opponent.SetOppGrenades(maxGrenades);
	// }
}