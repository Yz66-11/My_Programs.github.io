#pragma once
#include"camera.h"
#include<graphics.h>
class Scene 
{
public:
	Scene() = default;
	~Scene() = default;
	virtual void enter() {}
	virtual void update(int delta) {}
	virtual void draw(const Camera& camera) {}
	virtual void input(const ExMessage& msg) {}
	virtual void exit() {}
private:
	
};