#pragma once
#include"scene.h"

extern Scene* menu_scene;
extern Scene* game_scene;
extern Scene* selector_scene;
class SceneManager
{
public:
	enum class Tscene
	{
		Menu,
		Game,
		Selector
	};
	SceneManager() = default;
	~SceneManager() = default;
	void set_current_scene(Scene* scene)
	{
		current_scene = scene;
		current_scene->enter();
	}
	void switch_to(Tscene type)
	{
		current_scene->exit();
		switch (type)
		{
		case Tscene::Menu:
			current_scene = menu_scene;
			break;
		case Tscene::Game:
			current_scene = game_scene;
			break;
		case Tscene::Selector:
			current_scene = selector_scene;
			break;
		default:
			break;
		}
		current_scene->enter();
	}
	void update(int delta)
	{
		current_scene->update(delta);
	}

	void draw(const Camera& camera)
	{
		current_scene->draw(camera);
	}

	void input(const ExMessage& msg)
	{
		current_scene->input(msg);
	}

private:
	Scene* current_scene = nullptr;
};