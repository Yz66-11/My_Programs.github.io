#pragma once
#include"util.h"
#include"camera.h"
#include<graphics.h>

extern bool is_debug;

class Platform
{
public:
	Platform() = default;
	~Platform() = default;

	struct Collisionshape
	{
		float y = 0;
		float left = 0, right = 0;

	};
	Collisionshape shape;
	IMAGE* img = nullptr;
	POINT render_position = { 0 };
	void draw(const Camera& camera) const
	{
		putimage_alpha(camera, render_position.x, render_position.y, img);

		if (is_debug)
		{
			setlinecolor(RGB(255, 0, 0));
			line(camera, (int)shape.left, (int)shape.y, (int)shape.right, (int)shape.y);
		}
	}
private:
	
};