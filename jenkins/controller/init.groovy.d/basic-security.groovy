import jenkins.model.Jenkins
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm

def instance = Jenkins.get()

def adminUser = System.getenv("JENKINS_ADMIN_ID") ?: "admin"
def adminPassword = System.getenv("JENKINS_ADMIN_PASSWORD") ?: "change-me-jenkins"

def hudsonRealm = new HudsonPrivateSecurityRealm(false)
if (hudsonRealm.getUser(adminUser) == null) {
    hudsonRealm.createAccount(adminUser, adminPassword)
}

instance.setSecurityRealm(hudsonRealm)

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

instance.setNumExecutors(0)
instance.save()

println("--> Jenkins local-lab security and controller executor policy applied")
