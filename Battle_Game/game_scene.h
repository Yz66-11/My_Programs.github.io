#pragma once
#include"util.h"
#include"scene.h"
#include"player.h"
#include"status_bar.h"
#include"platform.h"
#include"scene_manager.h"
#include<windows.h>
#include<iostream>

extern IMAGE img_sky;
extern IMAGE img_hills;
extern IMAGE img_platform_large;
extern IMAGE img_platform_small;
extern IMAGE img_1P_winner;
extern IMAGE img_2P_winner;
extern IMAGE img_winner_bar;

extern std::vector<Platform> platform_list;
extern Camera main_camera;

extern Player* P1;
extern Player* P2;

extern IMAGE* img_P1_avatar;
extern IMAGE* img_P2_avatar;

extern SceneManager scene_manager;
class GameScene : public Scene
{
public:
	GameScene() = default;
	~GameScene() = default;

	void enter()
	{
		is_game_over = false;
		is_slideout_started = false;

		pos_img_winner_bar.x = -img_winner_bar.getwidth();
		pos_img_winner_bar.y = (getheight() - img_winner_bar.getheight()) / 2;
		pos_x_img_winner_bar_dst = (getwidth() - img_winner_bar.getwidth()) / 2;

		pos_img_winner_text.x = pos_img_winner_bar.x;
		pos_img_winner_text.y = (getheight() - img_1P_winner.getheight()) / 2;
		pos_x_img_winner_text_dst = (getwidth() - img_1P_winner.getwidth()) / 2;

		timer_winner_slidein.restart();
		timer_winner_slidein.set_wait_time(2500);
		timer_winner_slidein.set_one_shot(true);
		timer_winner_slidein.set_callback([&]()
			{
				is_slideout_started = true;
			});

		timer_winner_slideout.restart();
		timer_winner_slideout.set_wait_time(1000);
		timer_winner_slideout.set_one_shot(true);
		timer_winner_slideout.set_callback([&]()
			{
				scene_manager.switch_to(SceneManager::Tscene::Menu);
			});

		status_1p.set_avatar(img_P1_avatar);
		status_2p.set_avatar(img_P2_avatar);

		status_1p.set_position(235, 625);
		status_2p.set_position(675, 625);

		P1->set_hp(100);
		P2->set_hp(100);
		P1->set_position(200, 50);
		P2->set_position(975, 50);
		pos_img_sky.x = (getwidth() - img_sky.getwidth()) / 2;
		pos_img_sky.y = (getheight() - img_sky.getheight()) / 2;

		pos_img_hills.x = (getwidth() - img_hills.getwidth()) / 2;
		pos_img_hills.y = (getheight() - img_hills.getheight()) / 2;

		platform_list.resize(4);
		Platform& large_platform = platform_list[0];
		large_platform.img = &img_platform_large;
		large_platform.render_position.x = 122;
		large_platform.render_position.y = 455;
		large_platform.shape.left = (float)large_platform.render_position.x + 30;
		large_platform.shape.right = (float)large_platform.render_position.x + img_platform_large.getwidth() - 30;
		large_platform.shape.y = (float)large_platform.render_position.y + 60;

		Platform& small_platform_1 = platform_list[1];
		small_platform_1.img = &img_platform_small;
		small_platform_1.render_position.x = 175;
		small_platform_1.render_position.y = 360;
		small_platform_1.shape.left = (float)small_platform_1.render_position.x + 40;
		small_platform_1.shape.right = (float)small_platform_1.render_position.x + img_platform_small.getwidth() - 40;
		small_platform_1.shape.y = (float)small_platform_1.render_position.y + img_platform_small.getheight() / 2;

		Platform& small_platform_2 = platform_list[2];
		small_platform_2.img = &img_platform_small;
		small_platform_2.render_position.x = 855;
		small_platform_2.render_position.y = 360;
		small_platform_2.shape.left = (float)small_platform_2.render_position.x + 40;
		small_platform_2.shape.right = (float)small_platform_2.render_position.x + img_platform_small.getwidth() - 40;
		small_platform_2.shape.y = (float)small_platform_2.render_position.y + img_platform_small.getheight() / 2;

		Platform& small_platform_3 = platform_list[3];
		small_platform_3.img = &img_platform_small;
		small_platform_3.render_position.x = 515;
		small_platform_3.render_position.y = 225;
		small_platform_3.shape.left = (float)small_platform_3.render_position.x + 40;
		small_platform_3.shape.right = (float)small_platform_3.render_position.x + img_platform_small.getwidth() - 40;
		small_platform_3.shape.y = (float)small_platform_3.render_position.y + img_platform_small.getheight() / 2;

		mciSendString(_T("play bgm_game repeat from 0"), NULL, 0, NULL);
	}

	void update(int delta)
	{
		P1->update(delta);
		P2->update(delta);

		main_camera.update(delta);

		bullet_list.erase(std::remove_if(
			bullet_list.begin(), bullet_list.end(),
			[](const Bullet* bullet)
			{
				bool deletable = bullet->check_can_remove();
				if (deletable)
				{
					delete bullet;
					return deletable;
				}
			}
		),
			bullet_list.end());

		for (Bullet* bullet : bullet_list)
		{
			bullet->update(delta);
		}

		const Vector2& position_1p = P1->get_position();
		const Vector2& velocity_1p = P1->get_velocity();
		const Vector2& position_2p = P2->get_position();
		const Vector2& velocity_2p = P2->get_velocity();
		
		if (velocity_1p.y >= 2.1)
		{
			P1->set_hp(0);
		}

		if (velocity_2p.y >= 2.1)
		{
			P2->set_hp(0);
		}
		
		if (P1->get_hp() <= 0 || P2->get_hp() <= 0)
		{
			if (!is_game_over)
			{
				mciSendString(_T("stop bgm_game"), NULL,0, NULL);
				mciSendString(_T("play ui_win from 0"), NULL, 0, NULL);
			}
			is_game_over = true;
		}

		status_1p.set_hp(P1->get_hp());
		status_1p.set_mp(P1->get_mp());
		status_2p.set_hp(P2->get_hp());
		status_2p.set_mp(P2->get_mp());

		if (is_game_over)
		{
			pos_img_winner_bar.x += (int)(speed_winner_bar * delta);
			pos_img_winner_text.x += (int)(speed_winner_text * delta);

			if (!is_slideout_started)
			{
				timer_winner_slidein.update(delta);
				if (pos_img_winner_bar.x > pos_x_img_winner_bar_dst)
				{
					pos_img_winner_bar.x = pos_x_img_winner_bar_dst;
				}
				if (pos_img_winner_text.x > pos_x_img_winner_text_dst)
				{
					pos_img_winner_text.x = pos_x_img_winner_text_dst;
				}				
			}
			else
				timer_winner_slideout.update(delta);
		}
	}

	void draw(const Camera& camera)
	{
		putimage_alpha(camera, pos_img_sky.x, pos_img_sky.y, &img_sky);
		putimage_alpha(camera, pos_img_hills.x, pos_img_hills.y, &img_hills);

		for (const Platform& platform : platform_list)
		{
			platform.draw(camera);
		}
		if (is_debug)
		{
			settextcolor(RGB(255, 0, 0));
			outtextxy(15, 15, _T("已开启调试模式，按‘Q’键关闭"));
		}
		P1->draw(camera);
		P2->draw(camera);

		for (const Bullet* bullet : bullet_list)
		{
			bullet->draw(camera);
		}

		if (is_game_over)
		{
			IMAGE* winner = &img_1P_winner;
			if (P1->get_hp() > 0)
				winner = &img_1P_winner;
			if(P2->get_hp() > 0)
				winner = &img_2P_winner;
			putimage_alpha(pos_img_winner_bar.x, pos_img_winner_bar.y, &img_winner_bar);
			putimage_alpha(pos_img_winner_text.x, pos_img_winner_text.y,winner);
		}
		else
		{
			status_1p.on_draw();
			status_2p.on_draw();
		}
	}

	void input(const ExMessage& msg)
	{
		P1->input(msg);
		P2->input(msg);

		switch (msg.message)
		{
		case WM_KEYUP:
			if (msg.vkcode == 0x51)
			{
				is_debug = !is_debug;
			}
			break;
		default:
			break;
		}
	}

	void exit()
	{
		delete P1;
		delete P2;
		P1 = nullptr;
		P2 = nullptr;

		is_debug = false;

		bullet_list.clear();
		main_camera.reset();
	}
private:
	POINT pos_img_sky = { 0 };
	POINT pos_img_hills = { 0 };
	POINT pos_img_winner_bar = { 0 };
	POINT pos_img_winner_text = { 0 };

	StatusBar status_1p;
	StatusBar status_2p;

	Timer timer_winner_slidein;
	Timer timer_winner_slideout;
	
	bool is_slideout_started = false;
	bool is_game_over = false;
	int pos_x_img_winner_bar_dst = 0;
	int pos_x_img_winner_text_dst = 0;
	const float speed_winner_bar = 3.0f;
	const float speed_winner_text = 1.5f;
};