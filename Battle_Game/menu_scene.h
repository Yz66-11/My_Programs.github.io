#pragma once
#include"scene.h"
#include"camera.h"
#include"timer.h"
#include"scene_manager.h"
#include"animation.h"
#include<iostream>


extern IMAGE img_menu_background;
extern SceneManager scene_manager;
class MenuScene : public Scene
{
public:
	MenuScene() = default;
	~MenuScene() = default;

	void enter()
	{
		mciSendString(_T("play bgm_menu repeat from 0"), NULL, 0, NULL);
	}

	void update(int delta)
	{
		
	}

	void draw(const Camera& camera)
	{
		putimage(0, 0, &img_menu_background);
	}

	void input(const ExMessage& msg)
	{
		if (msg.message == WM_KEYUP)
		{
			mciSendString(_T("play ui_confirm from 0"), NULL, 0, NULL);
			scene_manager.switch_to(SceneManager::Tscene::Selector);
		}
	}

	void exit()
	{
		
	}
private:
	
};