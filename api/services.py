def create_assignment_service(reequest, validated_data):
    assignment = Assignment.objects.filter(
        question=validated_data.get('question')).first()
    if assignment:
        raise ValidationError(
            'This assignment already exists!')
    auth_user = request.user
    validated_data["instructor"] = auth_user.instructor
    return Assignments.objects.create(validated_data)

"""
Hello. And welcome on this survey though, this video will be about the sandboxes. So what is the sandbox is it's a safe environment when you can work on your project.
So instead of work on your computer, you can walk on the sandboxes that does the same version and the same system as our checker.
So to access to the list of the sandboxes you have on the left, a tab with a button called sandboxes.
So you click on it for now. You don't have any running sandboxes. That's why you get this view to run one.
It's pretty easy. You click on Chrome project. It will give you the list of the project you are working on.
Then you say the project that you are working on. So let's take application server for, for me. Um, and then if you scroll a bit, you will see that for all the task, you will have a button called, get a sandbox.
So basically you just have to click on it to ask for some books. So here you have different system. We can provide you, you went to 1604 by default, or you can take a version with Peyton's 3.5 in fabric and puppet.
So for the example, I will take the first, uh, the first one. So once you have started it, you will have several, several informations about it.
So you can close this view and go back to the sandbox tab. So now we are running the sandbox. Uh, you can see that we have a first access to it.
So three buttons here, SSH, SFTP, and access what terminology. So the simple way to use it is just to click on access for what terminology, when you click on it, you have a remote chair, uh, on the system.
So you can start to type directly or your commands or accordingly in something in C if you prefer, you can access through SSH to the server.
So is purchasing simper. You have to click on the button, SSH, you run a shell. If you are on Mac windows or something else, it works.
So you just have to run a share and copy and paste the command. So one, once you copy and past it, it will ask you for the password of the machine.
So here you have, um, the host do user and the password. So I will just click on the password to copy it.
So click to copy, and then I will pass it to my share. Now I see that I am connected as route on my machine.
So the machine is not on your computer, but it's remote. So this is the way to access to it. But for the first few weeks, I think the best, uh, to, to it, it's just to click do a seminar.
So you don't have to take care of environment and everything. Um, so bigger folder, you are limited to three sandboxes.
So don't run everything at the same time. If you want to reset the machine, uh, you just have to click on stop, be careful because when you stop the sandbox, it will destroy it.
So let's say, um, I access to it. I I'm creating a file with the common touch.  if I lose the file, you can see that the fight is here.
Now I will destroy the machine. So it's stuffing the machine. Okay. If I want to spin up again, the machine is up now, so let's try to connect to it.
And if I lose the fight, I would see that my testify is not here anymore. So be careful because when you stop and you start to machine, it's not the same instance.
So it's one-to-one with the same way and the content will be raised at the end of the project. One, once it's done, you can just click on, stop and finish your projects.
"""